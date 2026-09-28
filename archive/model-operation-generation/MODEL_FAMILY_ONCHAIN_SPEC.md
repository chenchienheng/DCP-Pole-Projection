# Historical snapshot — MODEL_FAMILY_ONCHAIN_SPEC.md

> Lifecycle: `HISTORICAL_REFERENCE`
> Current authority: `false`
> Runtime: `false`
> Source commit: `303482894b099d071d2d62f7fd5cba9a32878c34`
> Source path: `MODEL_FAMILY_ONCHAIN_SPEC.md`
> Original Git blob: `b6031c2fc8acceec1c4c6b62367463dea7f88ba4`

This preserved body is evidence of an earlier design. Its commands, roles, schedules, status flags and next actions are historical, not instructions to execute. Use the directory [index](README.md) for successor context. The source body below is preserved verbatim.

<!-- BEGIN VERBATIM HISTORICAL BODY -->
# Model Family On-Chain Specification

> Durable specification for binding model families into the XLEN / Xuanling runtime.
> Purpose: prevent models from remaining floating capability surfaces with weak continuity, weak auditability, and high hallucination/drift risk.
>
> This note does **not** claim that any model becomes perfect or incapable of error.
> It defines how models become chain-bound, role-aware, and writeback-accountable.

---

## 0. Core Reading

A model should not be treated as:
- an absolute sovereign center
- a self-sufficient truth machine
- a floating capability surface with no durable return path

A model should be treated as:
- a differentiated subsystem cognition node
- a replaceable reasoning body
- a chain-bound operational family member
- a writeback-accountable contributor inside one main continuity order

---

## 1. Why Model On-Chain Is Needed

When a model is not chain-bound, common failure modes include:
- drift across sessions
- answer instability
- weak role orientation
- weak source grounding
- context evaporation
- hallucination amplification through unreturned outputs

Therefore model on-chain does not mean "put the model on a blockchain".
It means:

> bind model operation into the main continuity chain so that model behavior becomes auditable, role-aware, and returnable.

---

## 2. Minimal On-Chain Conditions for a Model

A model is considered on-chain only when all of the following are present:

1. **role binding**
   - what role is the model serving now?
   - reasoning node / drafting node / audit node / translation node / synthesis node / external view node

2. **window binding**
   - which runtime window owns the current invocation?

3. **source binding**
   - what source references, notes, documents, or evidence sets is the model allowed to operate from?

4. **output contract**
   - what output type is expected?
   - draft / audit / comparison / classification / extraction / synthesis / decision support

5. **writeback surface**
   - where must the result return?
   - repo artifact / issue / register / log / board / external view

6. **drift visibility**
   - how do we detect that the model output drifted, contradicted prior chain state, or exceeded scope?

Without these, the model may still be useful,
but it is not yet truly on-chain.

---

## 3. Model Family Reading

Models should not all be flattened into one generic AI category.
They should be read as families with differentiated strengths and failure modes.

Possible family roles include:
- reasoning family
- drafting family
- audit family
- extraction family
- synthesis family
- interface/dialogue family
- vision/multimodal family
- domain-specialized family

A family is not defined only by vendor or brand.
It is defined by:
- role suitability
- coupling bias
- error pattern
- replaceability
- writeback discipline

---

## 4. Model On-Chain Record Schema

Each on-chain model invocation should eventually be representable with fields such as:

- invocation_id
- model_family
- model_instance_or_surface
- owner_window
- structural_role
- source_refs
- allowed_scope
- expected_output_type
- writeback_surface
- confidence_statement
- contradiction_flag
- drift_flag
- escalation_needed
- last_verified_time

---

## 5. Output Contract Rule

A model output should not be treated as chain-safe merely because it is fluent.
It becomes chain-safer only when it includes or obeys:

- source anchoring
- scope discipline
- role discipline
- contradiction visibility
- writeback obligation

Recommended minimum output fields for high-value operations:
- source_ref
- current_role
- claim_type
- confidence_or_uncertainty
- mismatch_or_gap
- next_single_action
- return_target

---

## 6. Anti-Hallucination Reading

Model on-chain does not guarantee zero hallucination.
It reduces hallucination risk by changing the operating environment.

Instead of leaving the model in a floating response mode,
it binds the model into:
- evidence
- role
- window
- writeback
- contradiction detection
- comparative family cooperation

Therefore the practical anti-hallucination formula is:

**hallucination risk reduction = source binding + role binding + writeback + contradiction visibility + replaceable model cooperation**

---

## 7. Multi-Model Cooperation Rule

Multiple models should not be read as competitors only.
They can be chained through differentiated roles.

Examples:
- one model drafts
- one model audits
- one model extracts structured fields
- one model compares against prior writeback
- one model produces public-readable synthesis

This does not require platform collision.
It requires:
- one main continuity chain
- one writeback discipline
- one role-aware runtime frame
- replaceable reasoning bodies

---

## 8. Escalation and Arbitration Rule

When models disagree, the system should not default to chaos.
Disagreement should trigger:
1. contradiction flag
2. source comparison
3. role re-check
4. window ownership check
5. escalation back to `00` or relevant audit surface

This means disagreement becomes signal,
not immediate breakdown.

---

## 9. Practical Onboarding Order for Models

### Phase 1
- bind current primary model surface to writeback and artifact registers

### Phase 2
- add audit/comparison model role

### Phase 3
- add extraction/synthesis differentiated roles

### Phase 4
- add domain-specialized or multimodal subsystem roles

The goal is not model count.
The goal is controlled role differentiation.

---

## 10. Immediate Repository Implication

The repository should evolve toward model-aware registers such as:
- model family register
- invocation contract schema
- contradiction register
- output proof contract
- model-to-window ownership map

Without this, models remain tools.
With this, models begin to function as chain-bound subsystem cognition.

---

## 11. Suggested Next Artifacts

1. `MODEL_INVOCATION_CONTRACT.md`
2. `MODEL_FAMILY_REGISTER.md`
3. `MODEL_CONTRADICTION_REGISTER.md`
4. `EXTERNAL_NODE_ONCHAIN_SPEC.md`
5. `SCHEDULING_EFFECT_REGISTER.md`

---

## 12. Status

- model_on_chain_reading_persisted: true
- anti_hallucination_environment_rule_persisted: true
- multi_model_role_rule_persisted: true
- model_invocation_register_pending: true
- return_to_00: true
