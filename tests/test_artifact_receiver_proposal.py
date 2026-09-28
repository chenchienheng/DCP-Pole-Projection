"""Portable proposal export tests; no OpenClaw host or live-skill mutation."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile
from unittest.mock import patch

from tools.build_artifact_receiver_proposal import build_proposal

ROOT = Path(__file__).resolve().parents[1]
CHECKOUT = 'a' * 40  # Explicit synthetic archive provenance, not a Git receipt.


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class ArtifactReceiverProposalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.archive = self.home / 'source.zip'
        self.receipt = self.home / 'receipt.json'
        self.output = self.home / 'proposal'
        self.members = {p.relative_to(ROOT).as_posix(): p.read_bytes()
                        for p in (ROOT / 'dcp_kernel').rglob('*.py')}
        self.members['tools/verify_artifact_delivery.py'] = (ROOT / 'tools/verify_artifact_delivery.py').read_bytes()
        self.members['README.md'] = (ROOT / 'README.md').read_bytes()
        self.write_archive()

    def write_archive(self, extras=(), omit=()):
        with warnings.catch_warnings(), zipfile.ZipFile(self.archive, 'w', zipfile.ZIP_DEFLATED) as z:
            warnings.simplefilter('ignore', UserWarning)  # deliberate duplicate test input
            for name, raw in sorted(self.members.items()):
                if name in omit:
                    continue
                item = zipfile.ZipInfo(name)
                item.create_system = 3
                item.external_attr = (stat.S_IFREG | 0o644) << 16
                z.writestr(item, raw)
            for name, raw, mode in extras:
                item = zipfile.ZipInfo(name)
                item.create_system = 3
                item.external_attr = mode << 16
                z.writestr(item, raw)
        data = self.archive.read_bytes()
        self.expected = sha(data)
        self.metadata = dict(checkout=CHECKOUT, sha256=self.expected, size_bytes=len(data),
                             scope='TRACKED_SOURCE_CHECKOUT_NOT_RELEASE_APPROVAL')
        self.receipt.write_text(json.dumps(self.metadata), encoding='utf-8')

    def build(self, **changes):
        args = dict(source_archive=self.archive, source_receipt=self.receipt,
                    output=self.output, expected_checkout=CHECKOUT,
                    expected_archive_sha256=self.expected)
        args.update(changes)
        return build_proposal(**args)

    def test_fixed_source_bytes_normal_package_and_inactive_support_layout(self):
        m = self.build()
        self.assertEqual(m['state'], 'PREPARED_NOT_IMPORTED_OR_APPLIED')
        self.assertFalse(m['host_import_tested'])
        self.assertFalse(m['host_apply_requested'])
        self.assertFalse((self.output / 'SKILL.md').exists())
        self.assertIn('status: proposal', (self.output / 'PROPOSAL.md').read_text())
        for item in m['source_files']:
            target = ('references/source-readme.md' if item['source_path'] == 'README.md'
                      else 'scripts/' + item['source_path'])
            self.assertEqual((self.output / target).read_bytes(), self.members[item['source_path']])
        for p in self.output.rglob('*'):
            if p.is_file():
                self.assertFalse(p.stat().st_mode & 0o111)
                self.assertTrue(p.relative_to(self.output).parts[0] in ('PROPOSAL.md', 'scripts', 'references'))
                self.assertNotIn(b'\0', p.read_bytes())
                p.read_bytes().decode('utf-8')
        result = subprocess.run([sys.executable, '-I', str(self.output / 'scripts/verify_delivery.py'), '--help'],
                                cwd=self.home, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--resume', result.stdout)

    def test_manifest_binds_every_payload_and_export_is_reproducible(self):
        first = self.build()
        second_dir = self.home / 'proposal-two'
        self.assertEqual(self.build(output=second_dir), first)
        for item in first['payload_files']:
            raw = (self.output / item['path']).read_bytes()
            self.assertEqual((len(raw), sha(raw)), (item['size_bytes'], item['sha256']))
        a = {p.relative_to(self.output): p.read_bytes() for p in self.output.rglob('*') if p.is_file()}
        b = {p.relative_to(second_dir): p.read_bytes() for p in second_dir.rglob('*') if p.is_file()}
        self.assertEqual(a, b)

    def test_output_is_create_only_and_original_inputs_remain_unchanged(self):
        old = self.archive.read_bytes(), self.receipt.read_bytes()
        self.build()
        with self.assertRaisesRegex(ValueError, 'OUTPUT_EXISTS'):
            self.build()
        self.assertEqual(old, (self.archive.read_bytes(), self.receipt.read_bytes()))

    def test_wrong_trusted_hash_or_revision_is_not_rederived_from_input(self):
        with self.assertRaisesRegex(ValueError, 'HASH_MISMATCH'):
            self.build(expected_archive_sha256='0' * 64)
        with self.assertRaisesRegex(ValueError, 'BINDING_MISMATCH'):
            self.build(expected_checkout='b' * 40)
        self.assertFalse(self.output.exists())

    def test_invalid_checkout_or_hash_shape_is_rejected(self):
        for kwargs in ({'expected_checkout':'main'}, {'expected_archive_sha256':'latest'}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.build(**kwargs)
        self.assertFalse(self.output.exists())

    def test_strict_receipt_json_and_size_types(self):
        raw = self.receipt.read_text()
        for content in ('{"checkout":"a","checkout":"b"}', '[]', '{"x":NaN}',
                        json.dumps({**self.metadata, 'size_bytes': True})):
            with self.subTest(content=content):
                self.receipt.write_text(content)
                with self.assertRaises(ValueError):
                    self.build()
                self.assertFalse(self.output.exists())
        self.receipt.write_text(raw)

    def test_receipt_size_limit_precedes_parsing(self):
        self.receipt.write_bytes(b' ' * 65537)
        with self.assertRaisesRegex(ValueError, 'RECEIPT_SIZE_LIMIT'):
            self.build()
        self.assertFalse(self.output.exists())

    def test_source_symlink_is_rejected_without_following_it(self):
        link = self.home / 'source-link.zip'
        link.symlink_to(self.archive)
        with self.assertRaisesRegex(ValueError, 'SYMLINK'):
            self.build(source_archive=link)

    def test_unsafe_member_paths_rejected_before_output(self):
        for name in ('../escape.py', '/absolute.py', 'dcp_kernel//evil.py', 'dcp_kernel/../evil.py', 'dcp_kernel\\evil.py'):
            with self.subTest(name=name):
                self.write_archive(extras=[(name, b'# no execution\n', stat.S_IFREG | 0o644)])
                with self.assertRaisesRegex(ValueError, 'UNSAFE_ARCHIVE_PATH'):
                    self.build()
                self.assertFalse(self.output.exists())
        self.assertFalse((self.home.parent / 'escape.py').exists())

    def test_duplicate_paths_cannot_select_last_value(self):
        self.write_archive(extras=[('dcp_kernel/__init__.py', b'# replacement', stat.S_IFREG | 0o644)])
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_ARCHIVE_PATH'):
            self.build()
        self.assertFalse(self.output.exists())

    def test_symlink_and_executable_payload_modes_are_not_packaged(self):
        for mode in (stat.S_IFLNK | 0o777, stat.S_IFREG | 0o755):
            with self.subTest(mode=mode):
                self.write_archive(extras=[('dcp_kernel/addition.py', b'# text\n', mode)])
                with self.assertRaises(ValueError):
                    self.build()
                self.assertFalse(self.output.exists())

    def test_hidden_null_and_non_utf8_payloads_are_rejected(self):
        for name, raw in (('dcp_kernel/.hidden.py', b'# hidden'),
                          ('dcp_kernel/null.py', b'\0'), ('dcp_kernel/binary.py', b'\xff')):
            with self.subTest(name=name):
                self.write_archive(extras=[(name, raw, stat.S_IFREG | 0o644)])
                with self.assertRaises(ValueError):
                    self.build()
                self.assertFalse(self.output.exists())

    def test_missing_required_existing_receiver_is_not_fabricated(self):
        self.write_archive(omit=['dcp_kernel/artifact_receiver.py'])
        with self.assertRaisesRegex(ValueError, 'REQUIRED_SOURCE_MISSING'):
            self.build()

    def test_member_and_payload_size_limits(self):
        with patch('tools.build_artifact_receiver_proposal.MAX_MEMBERS', 2):
            with self.assertRaisesRegex(ValueError, 'SOURCE_MEMBER_LIMIT'):
                self.build()
        with patch('tools.build_artifact_receiver_proposal.MAX_PAYLOAD_BYTES', 2):
            with self.assertRaisesRegex(ValueError, 'PAYLOAD_SIZE_LIMIT'):
                self.build()
        self.assertFalse(self.output.exists())

    def test_portable_cli_fresh_process_delivery_resume_and_corruption(self):
        self.build()
        outside = self.home / 'outside'; outside.mkdir()
        source = outside / 'source'; source.mkdir()
        received = outside / 'received'; received.mkdir()
        content = b'synthetic delivery; real independent processes\n'
        for directory in (source, received):
            (directory / 'report.txt').write_bytes(content)
        contract = outside / 'expected.json'
        contract.write_text(json.dumps(dict(delivery_id='test-delivery', source_id='test-source',
                          source_revision='r1', receiver='test-receiver',
                          artifacts=[dict(path='report.txt', size_bytes=len(content), sha256=sha(content))],
                          manual_interventions=['explicit test initiation'])))
        launcher = self.output / 'scripts/verify_delivery.py'
        def command(*args):
            return subprocess.run([sys.executable, '-I', str(launcher), *map(str,args)],
                                  cwd=outside, env={k:v for k,v in os.environ.items() if k != 'PYTHONPATH'},
                                  capture_output=True, text=True, timeout=10)
        pending, checked, again = (outside / n for n in ('pending.json', 'checked.json', 'again.json'))
        self.assertEqual(command('prepare', '--contract',contract,'--root',source,'--output',pending).returncode,0)
        common = ('receive','--contract',contract,'--root',received,'--pending',pending,'--output',checked)
        self.assertEqual(command(*common).returncode, 0)
        before = checked.read_bytes(), checked.stat().st_mtime_ns
        self.assertEqual(command(*common, '--resume').returncode,0)
        self.assertEqual((checked.read_bytes(), checked.stat().st_mtime_ns), before)
        self.assertEqual(command('receive','--contract',contract,'--root',received,'--pending',checked,'--output',again).returncode,0)
        self.assertEqual(again.read_bytes(), checked.read_bytes())
        state = json.loads(checked.read_text())
        self.assertEqual(state['result']['decision'], 'PASS')
        self.assertIn('NOT_SEMANTIC', state['scope'])
        self.assertIn('explicit test initiation', state['result']['return_closure']['manual_interventions'])
        (received/'report.txt').write_bytes(b'X'+content[1:])
        failed = command('receive','--contract',contract,'--root',received,'--pending',checked,'--output',outside/'held.json')
        self.assertEqual(failed.returncode,3,failed.stderr)
        self.assertEqual(json.loads((outside/'held.json').read_text())['result']['decision'],'HOLD')
        self.assertEqual((source/'report.txt').read_bytes(),content)
        self.assertEqual(checked.read_bytes(),before[0])


if __name__ == '__main__':
    unittest.main()
