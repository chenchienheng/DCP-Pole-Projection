# Discontinuity Register

> Lifecycle: `HISTORICAL_REFERENCE`
> Current authority: `false`
> Runtime: `false`
> Reader path: `REMOVED`

> Initial discontinuity register for repository weaving.
> This document does not treat every gap as a defect.
> Some gaps are normal because the broader Xuanling / XLEN system is still being constructed.
> The purpose here is to distinguish between:
>
> - normal construction-stage incompleteness
> - harmful discontinuity that blocks continuity or writeback

---

## 0. Register Status

- register_version: v0.1
- scope: currently verified repository artifacts and known structural gaps
- intent: mark gaps without pretending the system should already be finalized

---

## 1. Gap Types

### 1.1 Normal Construction Gap
A gap that is expected because the system is still being built.
It should be supplemented, not misread as system failure.

### 1.2 Harmful Discontinuity
A gap that causes session reset, role drift, loss of continuity, or inability to write back reliably.
These require priority remediation.

### 1.3 Ambiguous / Unverified Gap
A gap that is suspected but has not been fully verified in the repository during the current session.
These should be marked honestly, not guessed.

---

## 2. Initial Register

| ID | Gap / Discontinuity | Type | Current Effect | Current Treatment | Status |
|---|---|---|---|---|---|
| D-001 | No durable repository re-entry note existed before this historical round | Historical discontinuity | new sessions had higher re-entry cost | superseded by the repository-local Manifest plus a bounded REENTRY_ONLY surface | historical |
| D-002 | No bounded GitHub role map existed before this historical round | Historical discontinuity | GitHub role could collapse into a flat repository or privileged bone model | former master map retired from main; lineage remains in the existing re-entry archive index | historical |
| D-003 | No initial corpus index existed before this historical round | Historical discontinuity | verified artifacts and gaps were not durably separated | corpus index retained for lineage/discovery only; it does not establish Current | historical |
| D-004 | No role classification table existed before this session | Harmful Discontinuity | role drift risk across documents and sessions | remediated by `ROLE_CLASSIFICATION_TABLE.md` | addressed |
| D-005 | Full historical corpus inventory not yet verified repo-wide | Ambiguous / Unverified Gap | cannot yet claim repository-wide weave completeness | requires full file tree or equivalent inventory source | addressed |
| D-006 | 200+ historical documents not yet durably woven into one repository-wide index | Normal Construction Gap + Harmful Discontinuity | large body may exist, but cross-session continuity remains weak | continue with staged indexing and mapping | partially_addressed |
| D-007 | 12-window matrix not yet bound to durable repository artifact | Normal Construction Gap | higher-order runtime design not yet repo-bound | create `WINDOW_12_MASTER_TABLE.md` | addressed |
| D-008 | 64-gate binding note not yet persisted | Normal Construction Gap | transition/gating logic remains concept-heavy | create `GATE_64_BINDING_NOTE.md` | addressed |
| D-009 | three-coupling runtime map not yet persisted | Normal Construction Gap | link between bone/event/writeback remains incomplete at runtime-document level | create `THREE_COUPLING_RUNTIME_MAP.md` | pending |
| D-010 | broader external-node binding (web / workflow / collaboration surfaces) not yet normalized | Normal Construction Gap | external ecology remains partially connected and role-sensitive | create `EXTERNAL_NODE_ONCHAIN_SPEC.md` | pending |

| D-011 | Duplicate roles found in default writeback assignments across newly indexed files | Harmful Discontinuity | automated tagging caused minor overlap in classification | normalize default mapping in future script | pending |
| D-012 | Wording drift in chain classification | Ambiguous / Unverified Gap | some files default to Writeback Chain rather than clear event/bridge mapping | refine chain mapping heuristics | pending |

---

## 3. Reading Rule

This register should be read with the following rule:

- absence does not always equal defect
- evolving systems naturally contain staged incompleteness
- what matters is whether a gap has:
  - been named
  - been classified
  - been given a next binding action

If yes, the system is still coherent even when incomplete.

---

## 4. Current Priority Order

1. complete broader corpus indexing
2. persist three-coupling runtime map
3. persist 12-window master table
4. persist 64-gate binding note
5. normalize external node binding

---

## 5. Status

- harmful_discontinuities_partially_reduced: true
- normal_construction_gaps_acknowledged: true
- repository_weave_complete: false
- staged_continuity_repair_active: true
- return_to_00: true
