# External Node / Carrier Contract

> Lifecycle: `PUBLIC_RESEARCH_REFERENCE`
> Runtime: `false`
> Native source root: `false`
> Authority: `none`

This document preserves provider-neutral primitives for binding an external tool, service, model surface, repository, database, calendar, workflow system, human review surface, or other carrier into a bounded dependency chain.

## 1. Core rule
An external node is not trusted, authorized, or part of Runtime merely because it is connected.

`Connected != Authorized`
`Readable != Mutable`
`Capability != Authority`
`Available carrier != Native Source Root`
`Successful output != Reconciled world state`

## 2. Minimum binding fields
A material node binding should be representable with:
- `node_or_carrier_id`
- `provider_or_implementation`
- `capability_profile`
- `structural_role`
- `source_or_subject_refs`
- `receiver_or_owner`
- `input_boundary`
- `output_boundary`
- `rights_privacy_boundary`
- `action_authority`
- `evidence_or_receipt`
- `failure_modes`
- `fallback_or_replacement`
- `return_target`
- `reconciliation_requirement`
- `rebuild_or_exit_refs`
- `last_verified_revision_or_time`

`structural_role` states the node's bounded function in this particular binding. It is separate from available capabilities, semantic ownership and action authority; it does not establish a permanent role, fixed owner window or permission to act. A changed binding must re-evaluate the applicable role and boundaries.

## 3. Replaceability rule
A node should not become a hidden architecture root. Replacement readiness requires enough stable identity, interface expectation, evidence, return semantics, and rebuild/exit information to substitute or disable the carrier without redefining the governed object.

## 4. Failure rule
For material use, define:
- detectable failure condition;
- degraded/partial-result handling;
- retry or alternate carrier behavior;
- stale-state detection;
- irreversible-action boundary;
- evidence of what did or did not occur.

Failure that cannot be observed or reconstructed is more dangerous than ordinary unavailability.

## 5. Action and write-back gate
Read, transform, derive, learn, retain, mutate, write-back, delete, export, and share are separate rights. A connector or API exposing an operation does not grant permission to use it.

## 6. Return / reconciliation
Material node output should return as a typed result or receipt to its receiver. Return alone does not change Current. Any required admission, authority, evidence, or reconciliation gate still applies.

## 7. Provider examples
GitHub, Drive, Gmail, Calendar, Slack, Notion, workflow tools, databases, BIM/CDE systems, model APIs, sensors, and human review are implementation examples only. None defines the architecture primitive.

## 8. Historical compatibility
Earlier versions used `owner_window`, fixed writeback surfaces, GitHub as a bone/writeback anchor, and an “on-chain” framing. These remain historical implementation patterns, not universal invariants.
