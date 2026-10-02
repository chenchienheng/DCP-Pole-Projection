# Legacy-target handling — actual source rights before mutation

Status: CANDIDATE_REFERENCE / NOT_RUNTIME / NO_NEW_AUTHORITY.
Batch: BOARD_SOURCE_RETURN_CONTINUITY_20260928 (2026-09-28, Asia/Taipei).
Historical identifier: `RSP-003`; retained for traceability, not a current actor, role or permission.

## Purpose and target decision
Prevent an output from overwriting an inapplicable historical or protected source. Resolve the exact target identity, version, selected purpose and actual write authority before a mutation. The substring `v3`, an old filename or the word legacy alone does not decide every source's rights; equally, `relay_mode` alone grants none.

## Retained migration form
When controlled migration is explicitly authorized, the original `legacy_source_path`, `extracted_node_key`, `new_target_path`, `writeback_key` and `migration_log_ref` can remain a compatibility form. Preserve the original source and loss/change record. Do not create a new object merely because its display name or carrier changes.

Read, interpretation, migration, overwrite and deletion are distinct operations. A source may be valid to read but not to mutate. A path lookup or declaration of a relay does not establish current permissions, target revision, reader fidelity or transport.

## Failure and return
If target identity, applicability, version or authority is unresolved, stop the affected write and report that precise condition; do not reroute every task to a fixed window or block independent authorized work. Retain an actual failure record without fabricating execution. The existing [writeback packet](../04_adapter-layer/writeback_packet_contract.md) and [write-intent assessment](../04_adapter-layer/writeback_gate_spec.md) separate proposed representation from input assessment; neither proves a provider write occurred.

## Source, applicability and recovery

The frozen #324 delta proposed deletion of this path; this batch does not apply that deletion. The [complete predecessor](https://github.com/chenchienheng/DCP-Pole-Projection/blob/b8e60f54bbbb8546a36952d0458318c4f70a7664/01_runtime-spine/legacy_writeback_block_rule.md) (Git blob `283656432c4caf225ee9fe63ca74a3b930960d19`) and the existing evidence package retain every prior field, example, status and dated instruction. Old W0/00–07/platform/axis labels apply only to their source-era profile; they do not define current topology or restore a task by being read. This correction changes reference content, not a live service, identity core, account or schedule. Restore only after comparing newer changes.

Repository ordinary reading remains selected by the [existing manifest](../CURRENT-SURFACE-MANIFEST.json); a reference link or a successful check does not grant reader membership, execution, merge, deletion or publication approval.
