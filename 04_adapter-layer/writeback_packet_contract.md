# Write intent representation — purpose-bound compatibility reference

> Historical packet retained; not an active W0 protocol or universal transport shape.

## Existing candidate representation

Use `WriteIntentInput` in `dcp_kernel/write_intent.py` with `contracts/write-intent.schema.json`; qualification behavior is described in `writeback_gate_spec.md`. This is one existing candidate representation, not a requirement that every provider adopt its transport format.

Preserve intent/subject/source/target identities, mutation kind, applicable purpose/rights/authority, affected scope, revision where sensitive, fidelity/evidence plan, responsibility, recovery and receiver-specific return. Do not translate historical Department, Agent Block, W0 or ChatGPT fields into present identity or authority. GitHub is not a mandatory return destination.

Action names and booleans retain the existing schema's exact types: a string such as `"false"` is not a boolean authority assertion; an unknown action is not a supported mutation. A declared assertion is not verified permission. The packet does not authenticate external evidence, execute a write or prove receiver use.

## Selective source uptake

The same-path #324 source at `00999341ff600a65ab3de641e4ce5615d6e9690d` supplies the carrier-neutral intent distinction. Its three successor paths — module, schema and `tests/test_write_intent.py` — were checked in candidate `54cf305a89d9bcde2b88f1faa9a7566795c7155a`. This batch repairs input qualification in that module; it does not create a new adapter or import the whole source PR.

Ordinary reader membership still comes from `CURRENT-SURFACE-MANIFEST.json`; this compatibility reference is not added to that reader set. Current/public approval, deletion and external execution remain independently qualified.

## Provenance and complete predecessor

Selected source blob: `2eed504e1d1a452cc899e15db902b0d261f6f6fe`. Preserved predecessor at `54cf305a89d9bcde2b88f1faa9a7566795c7155a`: blob `b1d175745a9a08fe5129e4ab4a0702d0a909652f`, SHA256 `03e9076cd85f4b02496aa842fae79c4dde0edcfb4957bae65d4946741363d300`.

<details>
<summary>Complete historical predecessor — not current instructions</summary>

# Writeback Packet Contract

Department: Adapter Layer
Agent Block: Packet Contract
Node ID: ADP-006
Window: W0
Platform Writer: ChatGPT
Version: v0.1
Status: active

## Core
Every external writeback must use one packet shape.

## Required Fields
- department
- agent_block
- node_id
- window
- platform_writer
- source_object
- source_path
- target_path
- version
- log_ref
- timestamp
- action
- payload

## Action Types
- create
- update
- append_log
- sync_status

## Minimal Packet Example
```yaml
department: Adapter Layer
agent_block: Replit Relay
node_id: ADP-006
window: W0
platform_writer: ChatGPT
source_object: task_follow_up
source_path: 02_runtime-ops/task_follow_up.md
target_path: 02_runtime-ops/task_follow_up.md
version: v0.1
log_ref: LOG-0001
timestamp: 2026-04-09T00:00:00+08:00
action: update
payload:
  title: follow-up item
  status: open
  owner: runtime
```

## Validation Rule
Reject packet if any required field is missing.

## Return Rule
Successful writeback must append one log entry after write completes.

</details>
