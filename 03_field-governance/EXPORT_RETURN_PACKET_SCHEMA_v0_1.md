# Export and return — traceable delivery without automatic acceptance

Status: CANDIDATE_REFERENCE / NOT_RUNTIME / NO_NEW_AUTHORITY.
Batch: BATCH_FIELD_CONTINUITY_UPTAKE_20260928 (Asia/Taipei).

## Purpose and packet identity
An export packages a selected representation for an audience; a return conveys a result, correction, unresolved condition or actual effect to the relevant receiver. Preserve subject and packet identities, versions, applicable source and rights. A saved file is neither a new native source nor evidence that the receiver used it.

## Retained content contract
The compatibility form retains Export_Packet_ID, Packet_Title, evidence/view references, boundary statement, state, version/date and return fields. Keep what the output can and cannot support, material omissions or transformation losses, and the actual intended recipient. This is a selectable record profile, not a compulsory schema for every file or conversation.

Evidence_Index and Source_Class_Map may be references to authorized sources rather than duplicated datasets. Do not infer quality or approval from their presence. Keep authored time, source event/version, actual observation and recipient read time separate; unavailable times remain unknown.

## Destination and permissions
Decision_Log, Change_Log, QA_Gate, Return_Packet_Index, GitHub, Linear and QIN were one profile's possible targets, not a requirement to write all of them. Resolve the actual original deliverable and receiver. Each read, derive, retain, mutate, share and publish action has its own permission boundary. Exportable or public-safe does not mean approved to disclose.

## States and actual effects
Draft, Candidate, review and approved labels describe scoped dispositions, not a monotonic universal lifecycle. A document may be accepted for one use while another use remains held. Failed delivery, uncertain delivery and receiver rejection differ; a stored producer receipt alone cannot close them.

Before retrying a potentially performed mutation, inspect the known result and target state. Preserve conflicting evidence instead of overwriting it with a later success label. Rebuild from the appropriate valid checkpoint and accepted changes, not simply the newest packet.

## Examples and existing dependencies
Dashboard, strategy, consultant and QIN packets below retain concrete content concerns, not current deployment or professional acceptance. Charts need their source/date/aggregation basis; a capability report does not prove cooperation; a review packet does not grant publishing rights. Use only relevant [analysis](ANALYSIS_VIEW_MAP_v0_1.md) and [routing](MINIMAL_ROUTER_LAUNCHER_QIN_VIEW_GATE_v0_1.md) questions. Both files already exist; the predecessor's next split-out decision is not pending work.

## Closure and retention
Closure belongs to the named operation and acceptance condition. Some outputs need no further dispatch; where delivery/use/recovery is required, qualify it explicitly rather than fabricating acknowledgement. Retain the complete original schema and historical examples at the fixed predecessor; unique return semantics are not discarded or declared implemented by this rewrite.

## Retained compatibility forms

These uninstantiated source forms preserve compatible field names for a selected profile, not a required global schema or action grant. BASE/QIN, Window/Rank, named tables, mandatory_fields and destinations apply only to that explicitly chosen profile; do not create resources or infer approval to fill a form.

```yaml
Export_Return_Packet_Record:
  mandatory_fields:
    - Export_Packet_ID
    - Packet_Title
    - Packet_Type
    - Source_View_Refs
    - Evidence_Index_Refs
    - Boundary_Statement
    - Non_Approval_Disclaimer
    - Packet_State
    - Created_By
    - Created_At
    - Return_Packet_ID
    - Return_Path
  conditional_fields:
    - Decision_Log_ID
    - QA_Gate_ID
    - Change_Log_ID
    - Reviewer
    - Review_Status
    - Expiry_or_Review_By
```

```yaml
Evidence_Carry:
  Required:
    - Evidence_Index_Refs
    - Source_Class_Map
    - Evidence_Level_Map
    - Can_Support
    - Cannot_Support
    - Date_Basis_when_relevant
    - Data_Period_when_relevant
  Must_Not:
    - remove cannot-support statements
    - average evidence levels into unexplained confidence
    - cite view output as source when source evidence exists
    - allow unverified staging to appear as fact
```

```yaml
Boundary_Statement:
  Must_State:
    - what the packet can support
    - what the packet cannot support
    - which source/view layer it reads
    - which gates were passed
    - what remains pending or excluded
    - where correction or review returns
```

```yaml
Non_Approval_Disclaimer:
  Required_Distinctions:
    - Exportable is not approved
    - Readable is not validated
    - Market signal is not market validation
    - Capability is not cooperation willingness
    - Investment is not project opportunity
    - Matrix score is not approved recommendation
    - Dashboard state is not source of truth
    - Consultant pack is not doctrine
    - Public-facing output is not full dependency-chain disclosure
```

```yaml
Packet_State:
  - Draft
  - Candidate
  - Internal_Review
  - External_Review
  - Exported_Candidate
  - Returned_For_Revision
  - Superseded
  - Rejected
  - Archived
  - Approved_Only_If_Separately_Authorized
```

```yaml
Packet_Type: Dashboard_Export
Reads:
  - Governed_View
  - Fact_Table
  - Evidence_Index
Required:
  - evidence level carry
  - dashboard state boundary
  - return path
Forbidden:
  - treating dashboard state as source truth
```

```yaml
Packet_Type: Strategy_Report
Reads:
  - Strategy_PointCloud_View
  - Policy_Trend_View
  - Market_Signal_View
Required:
  - can_support / cannot_support
  - non-approval disclaimer
  - decision log reference if used in decision meeting
Forbidden:
  - turning signal map into approved strategy
```

```yaml
Packet_Type: Consultant_Pack
Reads:
  - Export_Packet_View
  - Evidence_Index
Required:
  - scope boundary
  - private/source limitation
  - return route for comments or revisions
Forbidden:
  - treating consultant-facing package as doctrine
```

```yaml
Packet_Type: QIN_Delivery_Packet
Reads:
  - QIN/View surface
  - governed view
  - evidence index
Required:
  - QIN_BASE_Six_Question trace
  - non-approval disclaimer
  - Return_Packet_ID
Forbidden:
  - letting QIN output bypass source/view, import/staging, or analysis-view gates
```

```yaml
Failure_Modes:
  Export_As_Approval:
    risk: packet movement is mistaken for decision authority
  Pretty_Report_No_Evidence:
    risk: presentation hides weak evidence
  Dashboard_As_Source:
    risk: view state overwrites source truth
  Consultant_Pack_As_Doctrine:
    risk: delivery surface becomes false governance rule
  Missing_Return_Path:
    risk: exported output cannot be corrected, revised, or audited
  Non_Approval_Disclaimer_Removed:
    risk: downstream overclaim
  Public_Output_Leaks_Dependency_Chain:
    risk: private or internal structure exposure
```

## Source and recovery

Selectively adapts [#324 fixed source](https://github.com/chenchienheng/DCP-Pole-Projection/blob/00999341ff600a65ab3de641e4ce5615d6e9690d/03_field-governance/EXPORT_RETURN_PACKET_SCHEMA_v0_1.md) (blob `10d62794e32e6a201f8f2b6f9d71511d8461557e`). [Complete predecessor](https://github.com/chenchienheng/DCP-Pole-Projection/blob/66099050d54a5ad533464cb4f28918fb04aadccb/03_field-governance/EXPORT_RETURN_PACKET_SCHEMA_v0_1.md) (blob `9e49982722eb37e84aac272bd91bd2e3405e6c81`) and the existing evidence package preserve every original form, example and dated decision. Historical labels/arrows are not current tasks, permission or a universal sequence. No source deletion, runtime, deployment or new authority follows. Restore only after checking newer changes; ordinary entry selection remains the [existing manifest](../CURRENT-SURFACE-MANIFEST.json).
