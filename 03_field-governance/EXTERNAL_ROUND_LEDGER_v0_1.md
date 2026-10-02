# External round ledger — compact evidence for resuming the same work

Status: CANDIDATE_REFERENCE / NOT_RUNTIME / NO_NEW_AUTHORITY.
Batch: BATCH_FIELD_CONTINUITY_UPTAKE_20260928 (Asia/Taipei).

## Purpose
A compact external record can help a new session locate the same authorized work, source versions, outcomes and unresolved dependencies. It does not by itself solve context drift or supersede the native Current.

## Continuation rule
Resolve the same subject and purpose from the applicable source, then use a relevant round record as evidence. The latest round or most recently modified file is not automatically Current. Remove the old restriction to continue only one Next_Task: an outstanding batch may contain several independent authorized actions, while a newer record may concern a different purpose.

Do not restart completed work from an earlier next-step field. Check whether an action already occurred before repeating it after interruption. Preserve conflicting or incomplete outcomes; absence of a receipt does not prove no execution. The ledger is neither an execution lease nor a task dispatcher.

## Record and time semantics
Keep the existing Round_Record and Round_Return_Packet field names for compatibility. Window is a carrier locator, not stable identity; Current_Node and Decision must bind their applicable source/version. Date must state whether it is record formation, source event or actual observation. Next_Task describes a remaining condition or action, not standing authorization.

For a real batch, Changed_Artifacts should point to the actual versions and effects; Open_Risks must remain scoped. Preserve last-valid state and enough information for recovery without requiring the next reader to load the full history.

## Storage and access
Choose a permitted persistent carrier for the actual purpose: an issue, document, task record or other native source may be appropriate. Platform names do not rank source authority. Do not place secrets, credentials, private identity lists, company-sensitive payloads or unapproved calibration material in this public repository.

## Return and completion
A persisted ledger can establish that a result was recorded; it does not prove dispatch, delivery, receiver read/use or integration acceptance. An old Needs_User_Decision value must be requalified for its unresolved decision, not used to demand acknowledgement after every increment. Correct a real misstatement in the original record or applicable continuation, keeping historical evidence and recovery available.

## Retained compatibility forms

These uninstantiated source forms preserve compatible field names for a selected profile, not a required global schema or action grant. BASE/QIN, Window/Rank, named tables, mandatory_fields and destinations apply only to that explicitly chosen profile; do not create resources or infer approval to fill a form.

```yaml
Round_Record:
  Round_ID:
  Window:
  Date:
  Current_Node:
  Decision:
  Changed_Artifacts:
  Open_Risks:
  Next_Task:
  Return_Path:
```

```yaml
Round_Return_Packet:
  Round_ID:
  What_Changed:
  What_Did_Not_Change:
  Decision:
  Needs_User_Decision: true | false
  Next_Round_Start_Prompt:
  Return_Path:
```

## Source and recovery

Selectively adapts [#324 fixed source](https://github.com/chenchienheng/DCP-Pole-Projection/blob/00999341ff600a65ab3de641e4ce5615d6e9690d/03_field-governance/EXTERNAL_ROUND_LEDGER_v0_1.md) (blob `e9544a307dcc4c3444296f9aab558f487684983a`). [Complete predecessor](https://github.com/chenchienheng/DCP-Pole-Projection/blob/66099050d54a5ad533464cb4f28918fb04aadccb/03_field-governance/EXTERNAL_ROUND_LEDGER_v0_1.md) (blob `fafecb4b15c4e93511e78f14832a23690ad55752`) and the existing evidence package preserve every original form, example and dated decision. Historical labels/arrows are not current tasks, permission or a universal sequence. No source deletion, runtime, deployment or new authority follows. Restore only after checking newer changes; ordinary entry selection remains the [existing manifest](../CURRENT-SURFACE-MANIFEST.json).
