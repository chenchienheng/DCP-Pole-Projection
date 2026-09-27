# MotherTree clearance — historical review record

> Applicability: historical reference; not an ordinary Current source or execution instruction.
> Runtime / Canon / new authority: not established by this document.

The queues, READY/HOLD values, merge order, named review roles, Seal/Keep_Editable lists and checked boxes below belong to the original review context. They are not live PR status, current release acceptance, write authority or a command to merge, close, rebase or delete anything.

Current work resolves the selected original PR/ref and `CURRENT-SURFACE-MANIFEST.json`; retain the original review as provenance where relevant. #324 proposed deleting this file; that deletion is not applied or approved here. A retained review record is not a current control plane.

## Provenance and preservation

Applicability reviewed against candidate `a53ea529e237f5a7e281c6cbb5d7380ca55f07e3` and its explicit manifest. This is a bounded candidate edit, not main adoption or source retirement.
Preserved predecessor: same path at `a53ea529e237f5a7e281c6cbb5d7380ca55f07e3`, blob `de2ad1b357fe75f881516d4dd5fd174a7831af7f`; SHA256 `befb925ad211f8a2dcecfdefca1cb662ab95fbe7f3c5b2e9a0cbc871db891ec5`.

<details>
<summary>Complete predecessor text — historical assertions, not current instructions</summary>

# MotherTree Clearance Report: Tri-coupled main upgrade

This report coordinates the repository hygiene and semantic doctrine triage
required to advance the `main` branch toward a tri-coupled baseline.

---

## Codex_Clearance_Report (Repo Hygiene)

### Queue_A: Mergeable Drafts
- **PR_124 (Cloud-over-Cloud):** **HOLD.** Substantially superseded by PR_131
  regarding the core specification. Recommend extracting unique relay/bridge
  language from #124 into #131 and closing #124.
- **PR_127 (Engineering Bridge):** **READY.** Clean against main. Safety
  boundaries (AUTHORIZED_WRITE = false) are correctly implemented.
- **PR_131 (Protocol Hardening):** **READY.** Provides the hardened version of
  the translation bridge spec and asset lifecycle matrix. Clean against main.

### Queue_B: Mergeable Non-Draft
- **PR_76 (Qinyi Submap):** **READY.** Clean against main. Scoped correctly as
  an external-facing subsystem.

### Queue_C: Blocked / Conflict Cleanup
- **PR_82 (Third Field):** **REBASE/CLEANUP.** Branch contains unrelated
  deletions of `docs/xuanling` files currently on `main`. Needs a clean rebase
  preserving existing `main` content.
- **PR_80 (Digital Twin Spec):** **SUPERSEDE.** A version of this spec already
  exists on `main`. PR_80 contains massive deletions of existing documentation.
- **PR_78 (Integration Card):** **REBASE/CLEANUP.** Similar to #82, contains
  unrelated deletions. Should be recreated as a clean patch against #76.
- **PR_75 (Three-State Model):** **REBASE/CLEANUP.** Messy branch with
  deletions. Needs to be cleaned to only include the new model file.

### Recommended_Merge_Order
1. PR #131 (Establishes hardened protocol/bridge spec)
2. PR #127 (Adds GAS engineering bridge)
3. PR #76 (Adds Qinyi submap)
4. (After cleanup) PR #82, #78, #75

### Risks
- **Diff Pollution:** Queue C PRs contain massive deletions of canonical
  documentation currently on `main`.
- **Semantic Overlap:** PR #124 and #131 both attempt to define the same
  Control Center spec; #131 is the more hardened version.

---

## Jules_Semantic_Report (Doctrine Boundary)

- **PR_124:** **Needs_Adjustment.** Core spec overlaps with #131. Wording
  is good but should be consolidated into the hardening PR.
- **PR_127:** **OK.** Strictly follows writeback/safety boundaries. Does not
  activate live automation by default.
- **PR_131:** **OK.** Correctly hardens asset lifecycle and return rules.
- **PR_76:** **OK.** Qinyi is treated as an external subsystem. Public/private
  boundary is respected.
- **PR_82:** **OK (Content-wise).** Third Field is properly mapped as a
  boundary/carrying layer.
- **PR_80:** **Hold.** Redundant with existing
  `XUANLING_VS_DIGITAL_TWIN_SPEC.md`.
- **PR_78:** **OK.** Complements #76 without redefining the full map.
- **PR_75:** **OK.** Positioning comparison only.

### Seal
- `00_mother-law/`
- `WORLD_CHAIN_MASTER_AXIS.md`
- `XUANLING_VS_DIGITAL_TWIN_SPEC.md` (Main version)

### Keep_Editable
- `04_adapter-layer/gemini_gas_sheet_bridge_spec.md`
- `docs/qinyi/`
- `02_translation-layer/`

---

## MotherTree Decision Rule Checklist
- [x] Repo hygiene is clean (for Queue A/B).
- [x] Semantic boundary is clean.
- [x] Public/private boundary is clean.
- [x] No Pending is promoted to Fact.
- [x] No external write is activated without authorization.
- [x] No subsystem replaces the mother architecture.
- [x] Every merged artifact has return path / registry entry.

</details>
