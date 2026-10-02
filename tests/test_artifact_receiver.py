from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from dcp_kernel.artifact_receiver import (
    ArtifactExpectation, ArtifactDeliveryContract, contract_from_dict,
    prepare_artifact_delivery, receive_artifact_delivery, pending_to_dict, pending_from_dict,
)
from dcp_kernel.models import Decision, ReturnState


class ArtifactReceiverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.src = self.home / 'source'; self.src.mkdir()
        self.dst = self.home / 'received'; self.dst.mkdir()
        self.raw = b'real expected bytes\n'
        for root in (self.src, self.dst):
            (root / 'report.txt').write_bytes(self.raw)
        self.contract = ArtifactDeliveryContract(
            'delivery-1', 'source-1', 'v1', 'LOCAL_DELIVERY_RECEIVER',
            (ArtifactExpectation('report.txt', hashlib.sha256(self.raw).hexdigest(), len(self.raw)),),
            ('user-requested local verification',),
        )

    def pending(self):
        return prepare_artifact_delivery(self.contract, self.src)

    def test_source_read_does_not_claim_delivery_acceptance(self):
        pending = self.pending()
        self.assertEqual(pending.decision, Decision.HOLD)
        self.assertEqual(pending.return_closure.state, ReturnState.PRODUCED)
        self.assertFalse(pending.return_closure.receiver_actual_read)
        self.assertEqual(pending.stable_life.current_revision, 'v1')

    def test_matching_received_files_are_really_read_twice_then_accepted(self):
        import dcp_kernel.artifact_receiver as receiver
        pending = self.pending()
        with patch.object(receiver, '_read_hash', wraps=receiver._read_hash) as reader:
            checked = receive_artifact_delivery(self.contract, pending, self.dst)
        self.assertEqual(reader.call_count, 2)
        self.assertEqual(checked.result.decision, Decision.PASS)
        self.assertEqual(checked.result.return_closure.state, ReturnState.RETESTED)
        self.assertEqual(checked.observations[0]['sha256'], self.contract.artifacts[0].sha256)
        self.assertIn('NOT_SEMANTIC', checked.scope)
        self.assertEqual(checked.result.return_closure.autonomy_level, 'A0_MANUAL_PROMPT_DEPENDENT')

    def test_same_size_corruption_is_rejected_without_changing_artifacts(self):
        pending = self.pending()
        wrong = b'X' + self.raw[1:]
        (self.dst / 'report.txt').write_bytes(wrong)
        checked = receive_artifact_delivery(self.contract, pending, self.dst)
        self.assertEqual(checked.result.decision, Decision.HOLD)
        self.assertIn('ARTIFACT_HASH_MISMATCH', checked.result.reasons)
        self.assertEqual((self.dst / 'report.txt').read_bytes(), wrong)
        self.assertEqual(checked.result.stable_life, pending.stable_life)

    def test_missing_file_is_not_accepted(self):
        pending = self.pending(); (self.dst / 'report.txt').unlink()
        result = receive_artifact_delivery(self.contract, pending, self.dst).result
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn('ARTIFACT_READ_FAILED_ERRNO_2', result.reasons)

    def test_invalid_expected_source_cannot_prepare_a_qualified_effect(self):
        (self.src / 'report.txt').write_bytes(b'X' + self.raw[1:])
        self.assertIsNone(self.pending().effect)

    def test_manifest_identity_receiver_or_revision_substitution_is_rejected_before_read(self):
        pending = self.pending()
        for delta in ({'source_id':'other'}, {'source_revision':'v2'},
                      {'receiver':'other'}, {'delivery_id':'other'}):
            with self.subTest(delta=delta), patch('dcp_kernel.artifact_receiver._read_hash', side_effect=AssertionError('must not read')):
                result = receive_artifact_delivery(replace(self.contract, **delta), pending, self.dst).result
                self.assertEqual(result.decision, Decision.HOLD)
                self.assertIn('ARTIFACT_DELIVERY_BINDING_MISMATCH', result.reasons)

    def test_manifest_change_cannot_follow_same_saved_pending(self):
        pending = self.pending()
        changed = replace(self.contract, artifacts=(replace(self.contract.artifacts[0], sha256='0'*64),))
        self.assertIn('ARTIFACT_DELIVERY_BINDING_MISMATCH', receive_artifact_delivery(changed,pending,self.dst).result.reasons)

    def test_saved_pending_json_roundtrip_and_repeated_acceptance_do_not_execute(self):
        raw = json.dumps(pending_to_dict(self.pending()))
        restored = pending_from_dict(json.loads(raw))
        with patch('dcp_kernel.artifact_receiver.run_local_cycle', side_effect=AssertionError('no replay')):
            first = receive_artifact_delivery(self.contract, restored, self.dst)
            again = receive_artifact_delivery(self.contract, first.result, self.dst)
        self.assertEqual(first, again)
        self.assertEqual((self.src / 'report.txt').read_bytes(), self.raw)
        self.assertEqual((self.dst / 'report.txt').read_bytes(), self.raw)

    def test_producer_flags_cannot_replace_received_bytes(self):
        pending = self.pending()
        forged = replace(pending, decision=Decision.PASS,
                         return_closure=replace(pending.return_closure,state=ReturnState.RETESTED,
                                                receiver_actual_read=True,rebuild_applied=True,
                                                native_disposition='USE_LOCAL_EFFECT',
                                                behavior_delta_observed=True,retested=True))
        (self.dst / 'report.txt').write_bytes(b'X' + self.raw[1:])
        result = receive_artifact_delivery(self.contract, forged, self.dst).result
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn('ARTIFACT_HASH_MISMATCH', result.reasons)

    def test_traversal_duplicate_and_boolean_size_fail_contract_validation(self):
        for path in ('../other', '/other', './report.txt', 'a//b', 'a\\b', ''):
            with self.subTest(path=path), self.assertRaises(ValueError):
                prepare_artifact_delivery(replace(self.contract, artifacts=(replace(self.contract.artifacts[0],path=path),)),self.src)
        with self.assertRaises(ValueError):
            prepare_artifact_delivery(replace(self.contract,artifacts=self.contract.artifacts*2),self.src)
        with self.assertRaises(ValueError):
            prepare_artifact_delivery(replace(self.contract,artifacts=(replace(self.contract.artifacts[0],size_bytes=True),)),self.src)

    def test_valid_empty_file_and_nested_paths(self):
        for root in (self.src,self.dst):
            (root/'nested').mkdir(); (root/'nested'/'empty').write_bytes(b'')
        contract=replace(self.contract, artifacts=(ArtifactExpectation('nested/empty',hashlib.sha256(b'').hexdigest(),0),))
        self.assertEqual(receive_artifact_delivery(contract,prepare_artifact_delivery(contract,self.src),self.dst).result.decision,Decision.PASS)

    @unittest.skipUnless(hasattr(os,'symlink'),'symlinks not available')
    def test_file_directory_and_root_symlinks_are_not_followed(self):
        pending=self.pending()
        (self.dst/'report.txt').unlink(); (self.dst/'report.txt').symlink_to(self.src/'report.txt')
        self.assertEqual(receive_artifact_delivery(self.contract,pending,self.dst).result.decision,Decision.HOLD)
        linked=self.home/'root-link'; linked.symlink_to(self.src,target_is_directory=True)
        self.assertEqual(receive_artifact_delivery(self.contract,pending,linked).result.decision,Decision.HOLD)
        (self.dst/'nested').symlink_to(self.src,target_is_directory=True)
        contract=replace(self.contract, artifacts=(replace(self.contract.artifacts[0],path='nested/report.txt'),))
        (self.src/'nested').mkdir(); (self.src/'nested'/'report.txt').write_bytes(self.raw)
        prepared=prepare_artifact_delivery(contract,self.src)
        self.assertEqual(receive_artifact_delivery(contract,prepared,self.dst).result.decision,Decision.HOLD)

    @unittest.skipUnless(hasattr(os,'mkfifo'),'FIFO not available')
    def test_fifo_does_not_block_or_get_accepted(self):
        pending=self.pending(); (self.dst/'report.txt').unlink(); os.mkfifo(self.dst/'report.txt')
        self.assertEqual(receive_artifact_delivery(self.contract,pending,self.dst).result.decision,Decision.HOLD)

    def test_changed_second_read_cannot_be_reported_as_retested(self):
        pending=self.pending()
        with patch('dcp_kernel.artifact_receiver._read_hash',side_effect=[{'sha256':'first'},{'sha256':'second'}]):
            result=receive_artifact_delivery(self.contract,pending,self.dst).result
        self.assertEqual(result.decision,Decision.HOLD)
        self.assertIn('ARTIFACT_READBACK_DRIFT',result.reasons)

    def test_contract_rejects_asserted_verification_fields(self):
        data=json.loads(json.dumps(asdict(self.contract))); data['verified']=True
        with self.assertRaises(TypeError): contract_from_dict(data)


class ArtifactReceiverPackageCliTests(unittest.TestCase):
    def test_normal_package_exports_receiver_and_existing_host(self):
        import dcp_kernel
        for name in ('ArtifactExpectation','ArtifactDeliveryContract','ArtifactDeliveryCheck',
                     'prepare_artifact_delivery','receive_artifact_delivery',
                     'run_local_cycle','reconcile_local_result','LocalExecutionRequest','EffectObservation'):
            self.assertTrue(hasattr(dcp_kernel,name),name)
            self.assertIn(name,dcp_kernel.__all__)

    def test_real_cli_prepare_receive_create_only_and_no_input_overwrite(self):
        from tools.verify_artifact_delivery import main
        with tempfile.TemporaryDirectory() as name:
            home=Path(name); src=home/'source'; dst=home/'received'; src.mkdir(); dst.mkdir()
            raw=b'CLI actual bytes\n'
            for root in (src,dst): (root/'report.txt').write_bytes(raw)
            contract=ArtifactDeliveryContract('cli','src','v1','receiver',
                (ArtifactExpectation('report.txt',hashlib.sha256(raw).hexdigest(),len(raw)),))
            manifest=home/'contract.json'; manifest.write_text(json.dumps(asdict(contract)))
            pending=home/'pending.json'; result=home/'accepted.json'
            self.assertEqual(main(['prepare','--contract',str(manifest),'--root',str(src),'--output',str(pending)]),0)
            args=['receive','--contract',str(manifest),'--root',str(dst),'--pending',str(pending),'--output',str(result)]
            self.assertEqual(main(args),0)
            self.assertEqual(json.loads(result.read_text())['result']['decision'],'PASS')
            before=result.read_bytes(); self.assertEqual(main(args),2); self.assertEqual(result.read_bytes(),before)
            args[-1]=str(dst/'report.txt'); self.assertEqual(main(args),2)
            self.assertEqual((dst/'report.txt').read_bytes(),raw)

    def test_cli_duplicate_json_keys_are_rejected(self):
        from tools.verify_artifact_delivery import _load
        with tempfile.TemporaryDirectory() as name:
            path=Path(name)/'bad.json'; path.write_text('{"delivery_id":"a","delivery_id":"b"}')
            with self.assertRaises(ValueError): _load(path)


if __name__=='__main__': unittest.main()
