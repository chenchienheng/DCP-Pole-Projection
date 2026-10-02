# Analysis views — preserve meaning from source to usable representation

Status: CANDIDATE_REFERENCE / NOT_RUNTIME / NO_NEW_AUTHORITY.
Batch: BATCH_FIELD_CONTINUITY_UPTAKE_20260928 (Asia/Taipei).

## Purpose
An analysis view is a purpose- and audience-specific interpretation or visualization. Its layout, file format and source table names do not make it authoritative. Select the actual source, applicable version, right to use it, and claim being evaluated. A source can support different views without forcing every view through one BASE/QIN database.

## Input and evidence suitability
Governed views and reviewed fact tables are useful inputs when their review covers the present claim. A raw import may be inspected in a clearly labelled diagnostic or review view, but must not silently become confirmed facts in an executive dashboard. Proposed IDs and unresolved aliases stay proposed until matching is justified. A company capability statement does not establish willingness to cooperate, and policy or investment news alone does not establish a project opportunity.

Source-class labels are not universal quality scores. Evidence level, date, scope and conflicts must be interpreted against the question. A newer timestamp is not automatic precedence; an attractive chart or matrix score is not a decision or approval.

## Chart, trend, matrix and dashboard behavior
Retain source references and material omissions. A trend needs a stated period, comparable units and a justified comparison basis. A matrix needs its chosen criteria, interpretation and uncertainty; weights must not silently change a candidate into fact. A dashboard distinguishes reported, pending, observed and accepted states and identifies stale observations. Never average incompatible evidence categories merely to produce one number.

The compatibility forms below preserve the original chart metadata, view map and worked examples. Policy_Event_Fact, Market_Signal_Fact, Entity_Master, Relation_Bridge and other named tables are examples from one implementation profile, not required global databases. A reader may use an appropriate source through another representation without changing its identity or rights.

## Interface, change and return
QIN is a historical interface label, not a permanent model, writer or authority. Separate reading, deriving, saving, mutating a source and publishing. A presentation must not rewrite its source merely to tell a cleaner story; an authorized source correction is a separate versioned action with evidence and propagation to affected views.

Bind the saved view or export to the original deliverable, source versions and actual receiver. Saving a dashboard does not prove receiver use. Preserve the last valid representation and enough transformation context to correct or regenerate it.

## Existing related references, not a new task queue
[Source/view](SOURCE_VIEW_GATE_v0_1.md), [import/identity](IMPORT_STAGING_AND_STABLE_ID_RULE_v0_1.md), [export/return](EXPORT_RETURN_PACKET_SCHEMA_v0_1.md) and [routing](MINIMAL_ROUTER_LAUNCHER_QIN_VIEW_GATE_v0_1.md) already exist. Use only their relevant questions. The old request to decide or create the next split-out document is superseded by those existing artifacts; no mandatory order, all-view review or new dashboard task is created here. The examples below are design examples, not executed tests or present business decisions.

## Retained compatibility forms

These uninstantiated source forms preserve compatible field names for a selected profile, not a required global schema or action grant. BASE/QIN, Window/Rank, named tables, mandatory_fields and destinations apply only to that explicitly chosen profile; do not create resources or infer approval to fill a form.

```yaml
Visualization_Rule:
  Chart:
    must_carry: source class, evidence level, date basis, boundary
  Trend:
    must_carry: data period, source continuity, uncertainty state
  Matrix:
    must_carry: scoring criteria, evidence level, reviewer boundary
  Dashboard:
    must_carry: view state, data freshness, pending/confirmed/rejected counts, return path
```

```yaml
Evidence_Level_Carry:
  Required_On_Output:
    - Evidence_Level
    - Source_Class
    - Date_Basis
    - Data_Period
    - Boundary_Statement
    - Return_Path
  Must_Not:
    - hide Pending state
    - average evidence levels into one confidence score without explanation
    - upgrade weak evidence through visualization design
    - remove cannot-support statements from decision views
```

```yaml
Analysis_View_Map:
  Strategy_PointCloud_View:
    reads:
      - Policy_Event_Fact
      - Market_Signal_Fact
      - Metric_TimeSeries_Fact
      - Evidence_Index
    purpose: strategic landscape and signal distribution
    boundary: signal map, not approved strategy by itself
  Policy_Trend_View:
    reads:
      - Policy_Event_Fact
      - Official_Source records
      - Metric_TimeSeries_Fact
    purpose: policy and regulation timeline
    boundary: policy direction is not project opportunity
  Market_Signal_View:
    reads:
      - Market_Signal_Fact
      - Evidence_Index
      - Source_Ledger
    purpose: market signal tracking
    boundary: signal is not validation
  Entity_Project_Map:
    reads:
      - Entity_Master
      - Project_Asset_Master
      - Relation_Bridge
    purpose: entity/project relation mapping
    boundary: relation is not cooperation willingness
  Capability_Ledger_View:
    reads:
      - Capability_Ledger
      - Evidence_Index
      - Relation_Bridge
    purpose: capability visibility
    boundary: capability is not commitment
  Governance_Dashboard:
    reads:
      - QA_Gate
      - Change_Log
      - Decision_Log
      - Return_Packet_Index
    purpose: review, change, closure, and return tracking
    boundary: dashboard state is not source fact
  Development_Candidate_View:
    reads:
      - Entity_Master
      - Capability_Ledger
      - Constraint_Gate
      - Relation_Bridge
    purpose: candidate development surface
    boundary: candidate is not approved partner
  Risk_Opportunity_Map:
    reads:
      - Constraint_Gate
      - Market_Signal_Fact
      - Evidence_Index
      - Decision_Log
    purpose: risk/opportunity interpretation
    boundary: opportunity candidate is not opportunity pipeline
```

```yaml
Failure_Modes:
  Pretty_Dashboard_Thin_BASE:
    risk: visuals look convincing but evidence support is weak
  Raw_Staging_In_Chart:
    risk: duplicate or unresolved records distort trends
  Matrix_As_Decision:
    risk: scoring becomes false approval
  Trend_As_Validation:
    risk: weak signal becomes strategic certainty
  Dashboard_As_Source:
    risk: view state overwrites source truth
  Evidence_Level_Dropped:
    risk: users cannot judge support strength
  No_Return_Path:
    risk: analysis cannot be corrected or audited
```

```yaml
Input: Policy_Event_Fact + Official_Source records
View: Policy_Trend_View
Allowed: chart timeline and signal concentration
Forbidden: claim confirmed project opportunity from policy alone
Gate: Evidence_Level_Carry + Source_View_Gate
Return: Decision_Log / Return_Packet_Index
```

```yaml
Input: Market_Signal_Fact + Evidence_Index
View: Market_Signal_View
Allowed: rank signals by evidence level and relevance
Forbidden: treat matrix score as approved recommendation
Gate: Evidence_Boundary + Analysis_View_Rule
Return: QA_Gate / Change_Log
```

```yaml
Input: Entity_Master + Project_Asset_Master + Relation_Bridge
View: Entity_Project_Map
Allowed: display reviewed relations
Forbidden: infer cooperation willingness without evidence
Gate: Relation_Bridge review + Source_View_Gate
Return: Decision_Log
```

```yaml
Input: QA_Gate + Change_Log + Return_Packet_Index
View: Governance_Dashboard
Allowed: show open/closed/pending status
Forbidden: treat dashboard state as original source
Gate: Return_Gate
Return: Change_Log / Return_Packet_Index
```

```yaml
Input: user asks QIN for market trend chart
View: QIN analysis surface
Allowed: read governed view and show evidence level
Forbidden: query raw staging and present it as fact
Gate: QIN_BASE_Six_Question_Gate + Analysis_View_Rule
Return: Decision_Log or micro-check task
```

## Source and recovery

Selectively adapts [#324 fixed source](https://github.com/chenchienheng/DCP-Pole-Projection/blob/00999341ff600a65ab3de641e4ce5615d6e9690d/03_field-governance/ANALYSIS_VIEW_MAP_v0_1.md) (blob `61c67d967dd8405985f38406cd0b6a234660f37a`). [Complete predecessor](https://github.com/chenchienheng/DCP-Pole-Projection/blob/66099050d54a5ad533464cb4f28918fb04aadccb/03_field-governance/ANALYSIS_VIEW_MAP_v0_1.md) (blob `690d3b603cdacbd748b48ab796a3f66977e9632a`) and the existing evidence package preserve every original form, example and dated decision. Historical labels/arrows are not current tasks, permission or a universal sequence. No source deletion, runtime, deployment or new authority follows. Restore only after checking newer changes; ordinary entry selection remains the [existing manifest](../CURRENT-SURFACE-MANIFEST.json).
