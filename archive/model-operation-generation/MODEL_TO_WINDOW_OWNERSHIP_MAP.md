# Historical snapshot — MODEL_TO_WINDOW_OWNERSHIP_MAP.md

> Lifecycle: `HISTORICAL_REFERENCE`
> Current authority: `false`
> Runtime: `false`
> Source commit: `3d1cbacd20b2f6d568e328183d7f7d699f56ddf4`
> Source path: `MODEL_TO_WINDOW_OWNERSHIP_MAP.md`
> Original Git blob: `9cd6eb00807aeff4e4bc0b552e7569aec3dfa6ad`

This preserved body is evidence of an earlier design. Its commands, roles, schedules, status flags and next actions are historical, not instructions to execute. Use the directory [index](README.md) for successor context. The source body below is preserved verbatim.

<!-- BEGIN VERBATIM HISTORICAL BODY -->
# Model to Window Ownership Map

> Durable mapping between model families and runtime windows.
> Purpose: prevent model usage from floating outside the 12-window runtime frame.

---

## 0. Core Reading

Model families must not operate without window ownership.
This map defines preferred bindings so:
- roles are stabilized
- drift is reduced
- scheduling can attach correctly
- writeback becomes consistent

---

## 1. Mapping Table

| Model Family | Primary Windows | Secondary Windows | Role Bias |
|---|---|---|---|
| reasoning | `05`, `11`, `00` | `03` | analysis / comparison / chain reading |
| drafting | `01`, `07`, `12` | `02` | articulation / external expression |
| audit | `00`, `08`, `11` | `05` | contradiction / verification |
| extraction | `02`, `03`, `08` | `01` | field extraction / grouping |
| synthesis | `11`, `05`, `00` | `07` | integration / folding |
| interface_dialogue | `02`, `07` | `03` | intake / clarification |
| vision_multimodal | `02`, `07`, `12` | `11` | visual interpretation |
| domain_specialized | varies | varies | domain-bound operations |

---

## 2. Binding Rule

Each invocation must:
- declare its owner_window
- match the family-window compatibility
- escalate if mismatch occurs

---

## 3. Mismatch Rule

If model family and window are misaligned:
- mark mismatch_or_gap
- reassign window OR change role
- do not silently proceed

---

## 4. Scheduling Implication

This mapping directly supports:
- `SCHEDULING_EFFECT_REGISTER.md`
- window-based cadence activation

---

## 5. Status

- model_window_map_created: true
- drift_reduction_binding_started: true
- scheduling_alignment_enabled: true
- return_to_00: true
