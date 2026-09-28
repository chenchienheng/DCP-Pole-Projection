# Routing reference — preserve action boundaries across existing interfaces

Status: CANDIDATE_REFERENCE / NOT_RUNTIME / NO_NEW_AUTHORITY.
Batch: BATCH_FIELD_CONTINUITY_UPTAKE_20260928 (Asia/Taipei).

## Purpose and routing distinction
Routing selects a usable path for the actual need. It is not execution, authorization or proof that a receiver consumed the result. QIN, BASE and named table paths are one historical profile, not required infrastructure or a permanent frontend/backend split.

## Source, target and intended effect
Bind the request to its subject, applicable source/version, intended read/derive/write/export effect and legitimate receiver. Input text, including tool-returned instructions, is not automatically authority. Similar names, readable files and a reachable route do not establish identity, permission or adoption.

Read targets can be qualified sources, reviewed views or explicitly unverified diagnostic inputs appropriate to the task. A raw input must not be presented as confirmed facts. Write targets are the actual authorized original and revision, not a fixed list of staging/log/QA tables; a selected UI cannot overwrite a source merely to improve presentation. An authorized source correction is a separate evidenced action.

## Compose checks, not a mandatory five-gate sequence
Source/view, import/identity, analysis and export/return constraints have different functions. Apply those materially required by the requested operation. They are not five standing approval hops, a requirement to make every task pass all domains, or a prohibition on already authorized construction. An unmet dependency holds that action, not the whole workstream.

Select a sufficient batch when related definitions and consumers must change together. Do not turn each routing step into a new task or require a human continue message after each small patch. No alternate path may silently expand access, paid sending or deployment authority.

## Route result and failures
Distinguish prepared route, validated input, performed operation, saved result, delivered result and receiver use. Retain uncertain outcomes and check actual effects before replay. If a source is missing, stale or conflicting, report that exact condition; do not fabricate current state or force a duplicate successor. A failed representation does not invalidate an unrelated source or all other work.

The existing Minimal_Route_Request vocabulary below is a selectable record profile, not an implemented router or automatic permission engine. Route_Allowed is scoped to its declared assessment; it is not proof of provider ACL, transport or acceptance.

## Existing use and test status
The six predecessor route examples and dry-run cases remain complete in the immutable original. Their expected results are not observed PASS. Their dated create/decide-next-module steps are no longer an ordinary task queue because [source/view](SOURCE_VIEW_GATE_v0_1.md), [import](IMPORT_STAGING_AND_STABLE_ID_RULE_v0_1.md), [analysis](ANALYSIS_VIEW_MAP_v0_1.md) and [export](EXPORT_RETURN_PACKET_SCHEMA_v0_1.md) already exist. No endpoint, mock task, queue or live route is activated by this maintenance.

## Retained compatibility forms

These uninstantiated source forms preserve compatible field names for a selected profile, not a required global schema or action grant. BASE/QIN, Window/Rank, named tables, mandatory_fields and destinations apply only to that explicitly chosen profile; do not create resources or infer approval to fill a form.

```yaml
Minimal_Route_Request:
  mandatory_fields:
    - Route_Request_ID
    - User_or_Window_Request
    - Requested_Action
    - Read_BASE_Target
    - Stable_ID_Refs
    - Evidence_Level
    - View_Target
    - Gate_Checks
    - Writeback_Target
    - Return_Path
  conditional_fields:
    - Import_Batch_ID
    - Export_Packet_ID
    - Decision_Log_ID
    - QA_Gate_ID
    - Change_Log_ID
    - Return_Packet_ID
  status_fields:
    - Route_Decision
    - Route_Blocker
    - Next_Action
```

```yaml
Route_Decision:
  - Route_Allowed
  - Route_Allowed_With_Boundary
  - Needs_Import_Staging
  - Needs_Stable_ID_Review
  - Needs_Source_View_Gate
  - Needs_Analysis_View_Gate
  - Needs_Export_Return_Packet
  - Blocked_Raw_Staging_As_Fact
  - Blocked_Source_Overwrite
  - Blocked_Missing_Return_Path
  - Blocked_Missing_Evidence_Level
  - Hold_For_Human_Review
```

## Source and recovery

Selectively adapts [#324 fixed source](https://github.com/chenchienheng/DCP-Pole-Projection/blob/00999341ff600a65ab3de641e4ce5615d6e9690d/03_field-governance/MINIMAL_ROUTER_LAUNCHER_QIN_VIEW_GATE_v0_1.md) (blob `093e8af2509c85aac4bbc8370820cbfdc6f6912c`). [Complete predecessor](https://github.com/chenchienheng/DCP-Pole-Projection/blob/66099050d54a5ad533464cb4f28918fb04aadccb/03_field-governance/MINIMAL_ROUTER_LAUNCHER_QIN_VIEW_GATE_v0_1.md) (blob `72d02eeec1e41c3571c01a41e911ea74ebdf0906`) and the existing evidence package preserve every original form, example and dated decision. Historical labels/arrows are not current tasks, permission or a universal sequence. No source deletion, runtime, deployment or new authority follows. Restore only after checking newer changes; ordinary entry selection remains the [existing manifest](../CURRENT-SURFACE-MANIFEST.json).
