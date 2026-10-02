# Import and stable identity — qualify mappings without forcing a new data store

Status: CANDIDATE_REFERENCE / NOT_RUNTIME / NO_NEW_AUTHORITY.
Batch: BATCH_FIELD_CONTINUITY_UPTAKE_20260928 (Asia/Taipei).

## Purpose and staging
An import is received material; staging describes its unqualified or pending use, not necessarily a physical Import_Staging table. Data can remain at its authorized source with a pointer and scoped review. Do not copy a private dataset into another carrier merely to satisfy a schema.

## Stable identity and conflicts
A proposed identifier is a proposed mapping, not a confirmed entity. Preserve source identity and revision, distinguish aliases from different subjects, and avoid name-only matching. Same display name does not prove identity; different carrier IDs do not necessarily prove different real objects. A correction to one mapping must preserve affected references or an explicit migration path.

The retained record and ID state forms below preserve original fields and vocabulary for compatible consumers. Stable_ID_Families is an optional profile, not a universal ontology. Do not mint IDs, create registries or promote records simply to fill every field. The actual source domain determines the legitimate identity and accepted changes.

## Evidence and admission
Source categories and evidence labels can help organize a review, but they cannot universally rank truth, supersede a newer valid source, or establish applicability. Separate a source's claim from a calculated or inferred result. Retain duplicates, conflicting versions and missing evidence until a purpose-specific disposition is justified.

Promotion to a selected fact/view/production use requires its actual conditions: qualified identity, applicable evidence, legitimate write authority, target/version, fidelity and receiver acceptance where required. These are related questions, not a compulsory database pipeline. A label such as reviewed or confirmed is not independent proof.

## Non-destructive effects and recovery
Before a real mutation, bind the exact target rather than an active-sheet/default fallback. Protect applicable revisions and distinguish planned changes from performed changes. Preserve formulas, types, units, non-target data and concurrent edits where relevant; no-deletion alone does not prove no semantic loss. Retain before-state and observed result sufficient for recovery. This document does not supply or enable such a writer.

## Interface and examples
An interface submission is not authority to import everything in it. Label diagnostics and proposed mappings clearly. The four original examples retained below illustrate dataset, company-name spreadsheet, extracted PDF table and interface intake concerns; they are not executed provider tests or authorization to use company records here.

[Source/view](SOURCE_VIEW_GATE_v0_1.md), [analysis](ANALYSIS_VIEW_MAP_v0_1.md) and [export/return](EXPORT_RETURN_PACKET_SCHEMA_v0_1.md) already exist. Their relevant constraints can be composed in the actual task; the old create-next-Analysis_View_Map instruction is not outstanding work.

## Retained compatibility forms

These uninstantiated source forms preserve compatible field names for a selected profile, not a required global schema or action grant. BASE/QIN, Window/Rank, named tables, mandatory_fields and destinations apply only to that explicitly chosen profile; do not create resources or infer approval to fill a form.

```yaml
Import_Staging_Record:
  mandatory_fields:
    - Import_Batch_ID
    - Import_Row_ID
    - Source_Origin
    - Submitted_By
    - Raw_File_or_URL
    - Intake_Date
    - Proposed_Source_ID
    - Proposed_Entity_ID
    - Evidence_Level
    - Review_Status
    - Return_Path
  conditional_fields:
    - Proposed_Project_ID
    - Proposed_Evidence_ID
    - Proposed_Relation_ID
    - Proposed_Capability_ID
    - Proposed_Constraint_ID
    - Proposed_Opportunity_ID
  output_fields_after_review:
    - Confirmed_Source_ID
    - Confirmed_Entity_ID
    - Confirmed_Project_ID
    - Confirmed_Evidence_ID
    - Confirmed_Relation_ID
    - Review_Decision
    - QA_Gate_ID
    - Change_Log_ID
```

```yaml
Stable_ID_Families:
  Source_ID: source identity
  Entity_ID: organization / agency / company / person / tool / region identity
  Project_ID: project, case, asset, packet, or event identity
  Evidence_ID: source-backed evidence object
  Relation_ID: relation bridge between source, entity, project, capability, or event
  Capability_ID: verified or candidate capability
  Constraint_ID: legal, tax, trade, certification, internal control, or responsibility boundary
  Opportunity_ID: opportunity candidate after evidence and gate review
  Return_Packet_ID: return/closure/version-traceable packet identity
```

```yaml
ID_State_Model:
  Proposed_ID:
    meaning: suggested by import, model extraction, user input, or preliminary mapping
    can_support:
      - staging review
      - duplicate search
      - alias check
      - candidate mapping
    cannot_support:
      - production view
      - export packet
      - decision claim
      - approved opportunity
  Confirmed_ID:
    meaning: stable identifier accepted after review
    can_support:
      - governed view
      - relation bridge
      - evidence index
      - dashboard aggregation
      - export packet when boundary is included
```

```yaml
Duplicate_Alias_Conflict_Rule:
  Duplicate_Candidate:
    condition: imported record appears to match an existing confirmed record
    action: hold promotion until duplicate check completes
  Alias_Candidate:
    condition: imported name differs but likely points to existing entity/source/project
    action: create alias bridge only after review
  Conflict:
    condition: imported record contradicts existing BASE record
    action: mark Hold or Needs_Human_Verification
  Rejected_Noise:
    condition: record is irrelevant, untraceable, or not source-safe
    action: retain reject reason without production exposure
```

```yaml
Review_Status:
  - Draft
  - Submitted
  - Needs_Clarification
  - Pending_Source_Attachment
  - Pending_ID_Match
  - Duplicate_Candidate
  - Alias_Candidate
  - Conflict
  - Accepted
  - Rejected
  - Hold

Review_Decision:
  - Confirmed_New_Record
  - Matched_Existing_Record
  - Alias_Merged
  - Duplicate_Rejected
  - Conflict_Hold
  - Rejected_Noise
  - Needs_Human_Verification
```

```yaml
Failure_Modes:
  Direct_To_BASE_Import:
    risk: source pollution and unrecoverable identity drift
  Proposed_ID_Treated_As_Confirmed:
    risk: false joins, duplicate entities, bad dashboards
  Spreadsheet_Treated_As_Source_Of_Truth:
    risk: user collection becomes unsupported fact
  Model_Extraction_Treated_As_Human_Verified:
    risk: automation output becomes false evidence
  Duplicate_Unresolved_But_Exposed:
    risk: double counting and false trend analysis
  Conflict_Forced_Into_View:
    risk: dashboard hides uncertainty
  No_Return_Path:
    risk: imported data cannot be corrected or audited
```

```yaml
Input: downloaded public dataset
Staging: Import_Staging
Proposed_ID: Proposed_Source_ID + Proposed_Entity_ID
Gate: source identity review + duplicate check
Promotion: Source_Ledger / Entity_Master after review
Return: Change_Log + QA_Gate
```

```yaml
Input: spreadsheet of company names and notes
Staging: Import_Staging
Proposed_ID: Proposed_Entity_ID
Gate: alias / duplicate / evidence-level review
Promotion: Entity_Master only after match or new-record decision
Forbidden: treating company list as market base without review
Return: Decision_Log / Return_Packet_Index
```

```yaml
Input: extracted table from PDF
Staging: Import_Staging
Proposed_ID: Proposed_Source_ID + Proposed_Evidence_ID
Gate: source attachment + extraction verification
Promotion: Evidence_Index after review
Forbidden: treating extraction as original source
Return: QA_Gate / Change_Log
```

```yaml
Input: user submits candidate source or row through QIN
Staging: Import_Staging
View: Import_Review_View
Gate: QIN_BASE_Six_Question_Gate + Source_View_Gate
Promotion: governed BASE only after review decision
Return: QIN task result + Return_Packet_Index
```

## Source and recovery

Selectively adapts [#324 fixed source](https://github.com/chenchienheng/DCP-Pole-Projection/blob/00999341ff600a65ab3de641e4ce5615d6e9690d/03_field-governance/IMPORT_STAGING_AND_STABLE_ID_RULE_v0_1.md) (blob `60d17baad82e016618fd06c3b3a6735491407861`). [Complete predecessor](https://github.com/chenchienheng/DCP-Pole-Projection/blob/66099050d54a5ad533464cb4f28918fb04aadccb/03_field-governance/IMPORT_STAGING_AND_STABLE_ID_RULE_v0_1.md) (blob `d370b5a25a73e8c2d5ab2d21e8c54015fab3bb4c`) and the existing evidence package preserve every original form, example and dated decision. Historical labels/arrows are not current tasks, permission or a universal sequence. No source deletion, runtime, deployment or new authority follows. Restore only after checking newer changes; ordinary entry selection remains the [existing manifest](../CURRENT-SURFACE-MANIFEST.json).
