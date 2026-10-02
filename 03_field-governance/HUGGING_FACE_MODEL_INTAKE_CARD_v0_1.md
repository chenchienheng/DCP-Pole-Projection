# Hugging Face intake card — retain the specialist profile without fixed roles

Status: CANDIDATE_REFERENCE / NOT_RUNTIME / NO_NEW_AUTHORITY.
Batch: BATCH_FIELD_CONTINUITY_UPTAKE_20260928 (Asia/Taipei).

## Purpose
This remains an optional Hugging Face-specific intake form. Its provider specialization is useful when that is the actual source; age or non-selection in another task is not a reason to retire the tool, discard the card, or convert every intake into a generic artifact.

## Source and intended use
Identify the exact repository, artifact kind, publisher, revision and proposed task. Record modality, language, architecture and resource requirements only as supported by the source. A model card, dataset card, Space, paper or benchmark has its own scope; popularity, open weights, or a successful demo do not establish unrestricted rights, deployment fitness or measured improvement on the user's task.

Keep source statements, our fitness inference and actual observed use separate. Retain limitations, missing values, intended input/output, provenance and license conditions. Never turn model identity into a permanent reasoning/audit/commander role. The selected structural role belongs to the individual use.

## Rights, resources and code
Retrieving metadata, downloading data, running code, enabling remote code, using a hosted service and redistributing an artifact are separate actions. This card authorizes none of them. For a real invocation, qualify the relevant revision, dependencies, execution boundary, data destination and resource commitment in that task. No credential or private/company payload belongs in this public card.

## Decision and continuation
Accept, hold or reject for the named use with evidence and a revisiting condition. A missing license or resource fact holds the dependent use, not all model research or other construction. A proposal is not an installed capability. Next_Scan or Next_Action fields below do not create recurring monitoring or a mandatory test.

## Retained field-level usefulness
The original HF_Intake_Card, HF_Intake_Output and return record are retained below as selectable templates. Keep exact repository IDs, source paths and field meanings where real consumers depend on them. Do not fill unknown context size, license, metric or cost from memory. Use the original artifact and source to requalify material changes; avoid duplicating one capability across several new registries.

## Retained compatibility forms

These uninstantiated source forms preserve compatible field names for a selected profile, not a required global schema or action grant. BASE/QIN, Window/Rank, named tables, mandatory_fields and destinations apply only to that explicitly chosen profile; do not create resources or infer approval to fill a form.

```yaml
HF_Intake_Card:
  Intake_ID:
  Repo_ID:
  Type: model | dataset | space | paper | doc
  Publisher:
  Source_URL:
  Source_ID:
  Task:
  Modality:
  Language:
  License:
  Architecture:
  Size:
  Context_Window:
  Capability:
  Limitations:
  Risk:
  Use_As:
  Do_Not_Use_As:
  Boundary_Level:
  Verification_Status:
  Decision_State: Intake | Candidate | Hold | Reject
  Return_Path:
```

```yaml
HF_Intake_Output:
  Intake_ID:
  Repo_ID:
  Type:
  Task:
  Capability_Summary:
  Boundary_Summary:
  License_Status:
  Risk_Level:
  Decision_State:
  Recommended_Next_Action:
  Return_Path:
```

```yaml
HF_Intake_Return_Packet:
  Intake_Batch:
  Items_Reviewed:
  Candidates:
  Holds:
  Rejects:
  Risks:
  Next_Scan:
  User_Decision_Needed:
  Return_Path:
```

## Source and recovery

Selectively adapts [#324 fixed source](https://github.com/chenchienheng/DCP-Pole-Projection/blob/00999341ff600a65ab3de641e4ce5615d6e9690d/03_field-governance/HUGGING_FACE_MODEL_INTAKE_CARD_v0_1.md) (blob `990555016ec81fb402861949f204f71e03a1402c`). [Complete predecessor](https://github.com/chenchienheng/DCP-Pole-Projection/blob/66099050d54a5ad533464cb4f28918fb04aadccb/03_field-governance/HUGGING_FACE_MODEL_INTAKE_CARD_v0_1.md) (blob `c9edfd9d9e33b115282bf07a9d8bfbda0107036b`) and the existing evidence package preserve every original form, example and dated decision. Historical labels/arrows are not current tasks, permission or a universal sequence. No source deletion, runtime, deployment or new authority follows. Restore only after checking newer changes; ordinary entry selection remains the [existing manifest](../CURRENT-SURFACE-MANIFEST.json).
