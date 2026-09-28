# External table import reference — preserved GAS draft, not an approved writer

Status: HISTORICAL_CODE_RETAINED / LIVE_USE_NOT_QUALIFIED / NO_EXECUTABLE_AUTHORITY.
Purpose: preserve the useful import draft, payload and failure evidence while preventing its old safety and merge claims from becoming current operating instructions.

## Preserved implementation, not discarded capability

The complete original JavaScript fence, JSON payload, formula-restoration logic and dated PR127/139 assessment remain in [the fixed predecessor](https://github.com/chenchienheng/DCP-Pole-Projection/blob/08eddfc06cbea9f6884200a247b21df83d8e39c3/04_adapter-layer/gemini_gas_sheet_bridge_spec.md), blob `8c6f20be4a52e7b3dd926a6f6dcdeb7359f00c6a`. The original code and sample payload were separately extracted and retained in the existing evidence package before this edit; no deployed script was inspected, changed, enabled or removed by this task.

The #324 source explicitly keeps reclaim on hold until unique implementation evidence is extracted. This review preserves that evidence; it does not infer physical deletion eligibility, source retirement or a replacement production adapter.

## Behavior examined on 2026-09-28

Six offline checks executed the exact extracted draft in Node v22.16.0 with synthetic rows and a mock SpreadsheetApp. No provider SDK, network, account, credential or real sheet was used. The live-write flag was changed only inside the isolated mock to inspect write behavior; the preserved source is unchanged.

| Check | Observed result | Meaning |
|---|---|---|
| Default report-only | Zero mock writes; result says success with planned added count and DRY_RUN_REPORT | The explicit dry-run label works; status/count alone is not evidence of a performed mutation |
| Older Fact versus newer Radar | Older incoming value overwrote newer stored value in the mock | Fixed label weight wins before date comparison; label strings are not verified source quality or applicability |
| Duplicate Entity_Name | Incoming entity B changed the first matching row A, including its ID | Display name matching does not establish stable entity identity |
| Missing target_path | Draft selected the active sheet | Exact target binding is not required by this implementation |
| Existing formula | Formula string survived the mocked setValues call | Formula restoration is useful, but this is not real Sheets or full-workbook validation |
| Concurrent unrelated edit | Whole-range write replaced the intervening value with its older snapshot | No version/conflict check protected that mock write |

Four checks expose counterexamples to safe current use; two preserve positive behavior. They are not six repaired-code tests, a deployed service audit or proof that real user data was corrupted. The actual function is `getUpdateMode`; the predecessor's suggested `shouldUpdate` test referred to a different name.

## Use and unresolved conditions

Retain non-destructive intent, formula preservation, payload provenance, scoped error reporting and explicit report-only operation as reusable requirements. Do not retain a universal Fact/Signal/Radar ranking, name-only matching, active-sheet fallback, AXIS-05 return, or the instruction that toggling a constant is sufficient to authorize live mutation.

The old design_complete, Stale_Overwrite_Prevented and Recommended_Action: Merge claims are historical assertions, not current acceptance. A future real table use must qualify identity and exact target, source applicability/conflicts, actual authority, concurrency/revision handling, formula and field fidelity, result/readback and recovery for that use. Merely avoiding row deletion does not establish non-destructive semantics.

The existing [writeback packet](writeback_packet_contract.md) and [write-intent assessment](writeback_gate_spec.md) distinguish declaration from action; they do not authenticate a Sheets account or supply the missing transport/version checks. No new table adapter or universal schema is introduced here. API versions, permissions, quota and costs remain unverified for a future integration; private/company payloads are not authorized for external use by this reference.

## Source uptake and recovery

Selectively adopts the purpose/authority distinctions in [the existing #324 source](https://github.com/chenchienheng/DCP-Pole-Projection/blob/00999341ff600a65ab3de641e4ce5615d6e9690d/04_adapter-layer/gemini_gas_sheet_bridge_spec.md), blob `898e2b2c596e3d8a51642b57c40f9ca197e01967`. It is not an exact whole-file import or whole-source acceptance. The complete predecessor remains at [the fixed parent](https://github.com/chenchienheng/DCP-Pole-Projection/blob/08eddfc06cbea9f6884200a247b21df83d8e39c3/04_adapter-layer/gemini_gas_sheet_bridge_spec.md); restore only after checking newer changes.

These references do not install tools, grant access, change a live service, or authorize publication, merge, deletion or deployment. [Directory entry](README.md) and the [existing register](../CAPABILITY_ABSORPTION_REGISTER.md) retain the scope; source-era successor arrows are not a compulsory runtime pipeline.
