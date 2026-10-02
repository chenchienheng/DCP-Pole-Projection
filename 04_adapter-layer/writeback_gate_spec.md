# Write intent qualification — purpose-bound compatibility reference

> Historical W0/ChatGPT/GitHub route retained below; not an active shared control path.

## Use the existing executable gate

Call `assess_write_intent` in `dcp_kernel/write_intent.py` using the existing `contracts/write-intent.schema.json`. The packet reference documents representation; this file explains qualification and its limits, not a second implementation.

Malformed field types and unknown actions return HOLD before operation-specific checks. Valid enum members and exact JSON action strings remain supported. Existing requirements are preserved:
- UPDATE, DELETE, APPEND and SYNC_STATE need a declared expected revision.
- UPDATE and DELETE need declared target existence equal to boolean true.
- UPDATE, DELETE and SYNC_STATE need declared rollback or recovery.
- CREATE does not require a pre-existing target or revision.

All candidate actions retain the source, rights, authority, purpose, affected-scope, fidelity/evidence, responsibility and return requirements. A gate PASS only qualifies the declared candidate; it does not fetch permissions, verify evidence, compare a provider's revision, perform a mutation or prove absorption/release.

The actual authorized writer must enforce the real provider/version guard, preserve the before-image, read back the result and return evidence to the applicable receiver. Failure holds only dependent mutation; it does not impose a global read-only state on independent authorized work. No silent reroute or fixed GitHub return is created.

## Selective source uptake

The same-path #324 source at `00999341ff600a65ab3de641e4ce5615d6e9690d` supplies the separation between candidate assessment and execution authority. The named module, schema and `tests/test_write_intent.py` exist in candidate `54cf305a89d9bcde2b88f1faa9a7566795c7155a`; this batch closes malformed-input acceptance, not external-provider validation.

Ordinary reader membership remains with `CURRENT-SURFACE-MANIFEST.json`; this reference is not newly admitted. No main adoption, source deletion, external operation or Runtime status is implied.

## Provenance and complete predecessor

Selected source blob: `a0e701d90948ce1afe7dcec91da4f6fcc681d921`. Preserved predecessor at `54cf305a89d9bcde2b88f1faa9a7566795c7155a`: blob `4f8e407a3d740db1d1922af5ec467a215796736b`, SHA256 `005028dd6f30d6aa8cd46afb472ce93f8c00a79a57f6ef552da65dfd693b4a29`.

<details>
<summary>Complete historical predecessor — not current instructions</summary>

# Writeback Gate Spec

Department: Adapter Layer
Agent Block: Writeback Gate
Node ID: ADP-004
Window: W0
Platform Writer: ChatGPT
Version: v0.1

## Core
All external writes must pass a gate before returning to GitHub.

## Gate Checks
- source ref exists
- target path exists
- version field exists
- log entry required

## Return Path
external layer -> gate check -> GitHub write -> log update

## Fail Rule
if any check fails, stop external write and return to read-only mode

</details>
