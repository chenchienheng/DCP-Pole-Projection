# Historical snapshot — MODEL_CONTRADICTION_REGISTER.md

> Lifecycle: `HISTORICAL_REFERENCE`
> Current authority: `false`
> Runtime: `false`
> Source commit: `3d1cbacd20b2f6d568e328183d7f7d699f56ddf4`
> Source path: `MODEL_CONTRADICTION_REGISTER.md`
> Original Git blob: `3b0865a6602b7a855d6485b810d858af454231c9`

This preserved body is evidence of an earlier design. Its commands, roles, schedules, status flags and next actions are historical, not instructions to execute. Use the directory [index](README.md) for successor context. The source body below is preserved verbatim.

<!-- BEGIN VERBATIM HISTORICAL BODY -->
# Model Contradiction Register

> Durable register for contradiction, drift, and disagreement across chain-bound model operations.
> Purpose: turn model disagreement into auditable signal rather than silent instability.

---

## 0. Core Reading

Model contradiction is not automatically failure.
It becomes dangerous only when it is:
- unmarked
- unreturned
- unowned
- unresolved

Therefore this register exists so model disagreement can be:
- visible
- classified
- routed
- compared
- escalated when necessary

---

## 1. Contradiction Classes

### 1.1 Source Contradiction
The model output conflicts with cited source material or durable artifact state.

### 1.2 Chain-State Contradiction
The model output conflicts with the current repository/runtime chain reading.

### 1.3 Role Contradiction
The model exceeded or violated its assigned role.
Example:
- a drafting role silently acting as sovereignty arbiter

### 1.4 Window Contradiction
The output belongs to a different owner window than the one declared.

### 1.5 Cross-Model Contradiction
Two or more model families produce materially incompatible outputs under the same task frame.

### 1.6 Confidence Contradiction
The model sounds certain where the evidence base is partial, weak, or explicitly incomplete.

---

## 2. Register Fields

Each contradiction event should eventually be representable with fields such as:

- `contradiction_id`
- `timestamp`
- `invocation_id`
- `model_family`
- `owner_window`
- `contradiction_class`
- `source_refs`
- `conflicting_artifact_or_state`
- `summary`
- `severity`
- `drift_flag`
- `escalation_needed`
- `resolution_mode`
- `writeback_surface`
- `last_review_state`

---

## 3. Severity Rule

### S0 — informative mismatch
Useful disagreement or small mismatch with low runtime risk.

### S1 — local contradiction
Impacts a note, classification, or local routing decision.

### S2 — runtime-affecting contradiction
Impacts chain logic, window routing, artifact role, or scheduling behavior.

### S3 — sovereignty/continuity contradiction
Threatens time-chain reading, central return logic, or durable writeback discipline.

---

## 4. Resolution Modes

Possible resolution modes include:
- `compare_sources`
- `recheck_role`
- `reassign_window`
- `downgrade_confidence`
- `rewrite_rebind`
- `escalate_to_00`
- `preserve_disagreement_as_signal`

---

## 5. Anti-Hallucination Rule

A contradiction event should be created when:
- evidence is insufficient but confidence remains high
- different model families diverge materially
- chain-bound artifacts are contradicted without explicit mismatch marking
- a model silently changes scope or role

This means contradiction registration is part of hallucination reduction.

---

## 6. Minimal Contradiction Packet

Recommended minimum packet:

```yaml
contradiction_id:
invocation_id:
model_family:
owner_window:
contradiction_class:
source_refs:
summary:
severity:
drift_flag:
escalation_needed:
resolution_mode:
writeback_surface:
```

---

## 7. Relation to Existing Artifacts

Read together with:
- `MODEL_FAMILY_ONCHAIN_SPEC.md`
- `MODEL_INVOCATION_CONTRACT.md`
- `MODEL_FAMILY_REGISTER.md`
- `THREE_COUPLING_RUNTIME_MAP.md`
- `DISCONTINUITY_REGISTER.md`

Together these establish:
- model family role
- invocation contract
- contradiction visibility
- escalation path

---

## 8. Immediate Next Artifact

- `MODEL_TO_WINDOW_OWNERSHIP_MAP.md`
- future machine-readable contradiction register layer

---

## 9. Status

- model_contradiction_register_created: true
- contradiction_classes_defined: true
- severity_rule_defined: true
- return_to_00: true
