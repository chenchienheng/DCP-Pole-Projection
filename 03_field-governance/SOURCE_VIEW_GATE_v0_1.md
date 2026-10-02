# Source and view — keep provenance, permissible transformations and claim scope

Status: CANDIDATE_REFERENCE / NOT_RUNTIME / NO_NEW_AUTHORITY.
Batch: BATCH_FIELD_CONTINUITY_UPTAKE_20260928 (Asia/Taipei).

## Source and view distinction
A source is the original evidence or recorded input for the selected claim; a view is its purpose-specific representation. These roles are relative to the claim. A tool execution log can be primary evidence of that execution while remaining insufficient to prove an external business outcome. No carrier, publisher class, format or visibility level alone establishes truth or authority.

One source can support several views. Preserve source identity, applicable revision, rights, provenance and material context. Do not overwrite or reword a source merely because a report needs a cleaner story. An authorized source correction is legitimate when source-side evidence, permission, revision and affected-view propagation are addressed; it is not prohibited simply because an interface initiated the request.

## Source classes and evidence
Official, company, public-database, internal-record, media, tool-generated and imported materials require different questions. An official statement supports what it actually states within its scope, not every inferred intention or opportunity. A company claim is not cooperation consent. A media signal is not automatically verified fact. Calculated and observed outputs retain their acquisition method.

The old A/B/C or default_evidence_level mapping is not a universal precedence order. Relevance, authority for the specific claim, time/version, unit/definition, contradictory evidence and known limitations must be considered. A newer source or stronger label does not automatically invalidate another context.

## Transformations and useful representations
Summarization, translation, filtering, aggregation, visualization and export may be appropriate when authorized and fit for purpose. Preserve what the transformation omitted or changed and enough source detail for verification. A derived view must not silently gain broader support or disclosure rights. Units, comparison basis and material uncertainty cannot be erased for readability.

Strategy, market, capability, governance, development, interface and export views are examples, not a compulsory global view taxonomy. Unreviewed material may appear in a clearly labelled diagnostic view; do not present it as a confirmed fact table or accepted executive decision.

## Interface and intake
QIN/View and BASE are profile-local names, not permanent authority or source hierarchy. Reading, triggering an already authorized operation, preparing a candidate and performing a mutation are distinct. User or external input must be qualified for the requested effect; availability and receipt do not grant permission.

For imports, distinguish proposed and accepted identity, aliases, conflicts, applicable source version and actual target. Staging is a qualification state, not a requirement to copy every source into one physical table. The preserved staging fields below are optional compatibility vocabulary.

## Dashboard, export and return
Carry the material source references, date basis, claim limits and review/release state into the output. Public-safe does not equal publication approval; successful export does not establish receiver use. Return a correction or effect to the actual authorized source/deliverable and affected receiver, retaining version and recovery evidence. Not every task requires a new export packet or all six BASE questions.

## Existing companion work
[Import/identity](IMPORT_STAGING_AND_STABLE_ID_RULE_v0_1.md), [analysis](ANALYSIS_VIEW_MAP_v0_1.md), [export/return](EXPORT_RETURN_PACKET_SCHEMA_v0_1.md) and [routing](MINIMAL_ROUTER_LAUNCHER_QIN_VIEW_GATE_v0_1.md) already exist. The old instruction to create the next split-out import rule is no longer pending. These companion references do not redefine the semantic core or add a universal approval sequence. Original detailed categories and six examples remain fully recoverable at the predecessor; retained record forms below preserve their material field requirements for selected consumers.

## Retained compatibility forms

These uninstantiated source forms preserve compatible field names for a selected profile, not a required global schema or action grant. BASE/QIN, Window/Rank, named tables, mandatory_fields and destinations apply only to that explicitly chosen profile; do not create resources or infer approval to fill a form.

```yaml
Import_Staging_Rule:
  Landing_Table: Import_Staging
  Required_Fields:
    - Import_Batch_ID
    - Source_Origin
    - Submitted_By
    - Raw_File_or_URL
    - Intake_Date
    - Proposed_Source_ID
    - Proposed_Entity_ID
    - Evidence_Level
    - Review_Status
  Gate:
    - source identity review
    - evidence level review
    - duplicate / alias check
    - stable ID match or create
    - source/view boundary assignment
```

```yaml
Dashboard_Report_Rule:
  Must_Display_Or_Carry:
    - source class
    - evidence level
    - data period or publication date when relevant
    - boundary statement
    - pending / confirmed / rejected state
    - return path
  Must_Not:
    - hide pending state
    - upgrade evidence level through visual design
    - merge unrelated sources without relation bridge
    - turn a signal into a fact
    - turn an analysis view into source of truth
```

```yaml
Export_Packet_Rule:
  Required_Fields:
    - Export_Packet_ID
    - Evidence_Index
    - Source_Class_Map
    - Boundary_Statement
    - Non_Approval_Disclaimer
    - Packet_State
    - Return_Packet_ID
  Required_Disclaimer:
    - Exportable does not mean approved.
    - Market signal does not mean market validation.
    - Capability does not mean cooperation willingness.
    - Investment does not mean project opportunity.
    - View does not overwrite source.
```

## Source and recovery

Selectively adapts [#324 fixed source](https://github.com/chenchienheng/DCP-Pole-Projection/blob/00999341ff600a65ab3de641e4ce5615d6e9690d/03_field-governance/SOURCE_VIEW_GATE_v0_1.md) (blob `d1dfdb386c6c0f99e23749b9d0c8f88f8a355626`). [Complete predecessor](https://github.com/chenchienheng/DCP-Pole-Projection/blob/66099050d54a5ad533464cb4f28918fb04aadccb/03_field-governance/SOURCE_VIEW_GATE_v0_1.md) (blob `a9a496f4076359485fa6ac95ab53fc0455aed67f`) and the existing evidence package preserve every original form, example and dated decision. Historical labels/arrows are not current tasks, permission or a universal sequence. No source deletion, runtime, deployment or new authority follows. Restore only after checking newer changes; ordinary entry selection remains the [existing manifest](../CURRENT-SURFACE-MANIFEST.json).
