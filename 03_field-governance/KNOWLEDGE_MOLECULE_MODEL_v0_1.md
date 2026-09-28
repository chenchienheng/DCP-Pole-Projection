# Knowledge units — reusable meaning with recoverable source context

Status: CANDIDATE_REFERENCE / NOT_RUNTIME / NO_NEW_AUTHORITY.
Batch: BATCH_FIELD_CONTINUITY_UPTAKE_20260928 (Asia/Taipei).

## Purpose and storage
A knowledge molecule is one possible bounded representation of reusable content. It does not replace full documents or require a new store. A paragraph, row, code fragment, geometry relation or other appropriate unit may serve the actual purpose while the complete lawful source remains available.

## Retained schema
The original field names below remain an optional compatibility form. Molecule_ID identifies this representation; Entity_ID and Claim_ID need justified bindings rather than name similarity. Source_ID must resolve the applicable source/version and enough context to interpret the claim. Role_ID, Vector_ID and Language_ID describe a selected view or use; they do not establish permanent roles or architecture categories.

## Evidence and recomposition
Can_Support and Cannot_Support constrain the claim. Weight_Profile is a declared local ranking method, not verified evidence strength, truth or approval. Boundary_Level is not a substitute for actual rights, purpose and authority. Keep contradictory sources and transformation loss visible; a retrieved fragment without context may be insufficient for a decision even when highly ranked.

Recompose eligible units for a named effect and audience without expanding their claims. Record which sources and versions contributed and which unresolved conditions remain. Successful summarization does not authorize retention, disclosure, model training or mutation of a native source.

## Return and completeness
Return the resulting representation to the original deliverable with its source and relevant recovery relationship. Preserve full evidence where needed rather than deleting context to make retrieval compact. The accompanying [recomposition reference](RECOMPOSITION_ENGINE_v0_1.md) is not a running engine; neither document installs a database, embedding service, loader or model.

## Retained compatibility forms

These uninstantiated source forms preserve compatible field names for a selected profile, not a required global schema or action grant. BASE/QIN, Window/Rank, named tables, mandatory_fields and destinations apply only to that explicitly chosen profile; do not create resources or infer approval to fill a form.

```yaml
Knowledge_Molecule:
  Molecule_ID:
  Entity_ID:
  Source_ID:
  Claim_ID:
  Role_ID:
  Vector_ID:
  Language_ID:
  Weight_Profile:
  Can_Support:
  Cannot_Support:
  Boundary_Level:
  Recompose_Use:
  Return_Path:
  Verification_Status:
```

## Source and recovery

Selectively adapts [#324 fixed source](https://github.com/chenchienheng/DCP-Pole-Projection/blob/00999341ff600a65ab3de641e4ce5615d6e9690d/03_field-governance/KNOWLEDGE_MOLECULE_MODEL_v0_1.md) (blob `681ab25ef4d09e4e0107f53159fa930f15b06ef2`). [Complete predecessor](https://github.com/chenchienheng/DCP-Pole-Projection/blob/66099050d54a5ad533464cb4f28918fb04aadccb/03_field-governance/KNOWLEDGE_MOLECULE_MODEL_v0_1.md) (blob `564a8fa9736d3723745d4c8ccf8e0cda43392772`) and the existing evidence package preserve every original form, example and dated decision. Historical labels/arrows are not current tasks, permission or a universal sequence. No source deletion, runtime, deployment or new authority follows. Restore only after checking newer changes; ordinary entry selection remains the [existing manifest](../CURRENT-SURFACE-MANIFEST.json).
