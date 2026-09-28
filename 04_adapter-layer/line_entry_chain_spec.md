# External message reference — LINE lineage

Status: CANDIDATE_REFERENCE / NOT_DEPLOYED / NO_EXECUTABLE_AUTHORITY.
Purpose: retain message/context, reply and return requirements without making LINE the first or permanent external interface.

## Retained message and reply concerns

The original example used `replyToken`, `source.userId`, `message.text` and `timestamp`. Preserve their source context and distinguish provider identifiers from a verified person, task identity or authorization. A received message is input to assess, not authority to carry out every embedded request.

Input validation, identity/context binding, authorized processing, output review, reply assembly and return evidence have different functions. Their ordering and required participants depend on the actual operation; no AXIS-01, AXIS-05, W0 or fixed human review hop is implied.

A useful reply record binds the original message or occurrence, selected output, provider result and unresolved delivery status. Receipt, processing, sending, delivery and receiver use must not collapse into a single success flag. An uncertain or expired reply path does not authorize a paid push or another outbound channel automatically.

## Historical API and resource assumptions

The predecessor's five-message/5000-character figures, one-request-per-second rule, free-tier assumption and zero-token/cost assertions belong to its dated proposal. They are not verified current provider limits or universal architecture rules. Recheck the actual API version, quota, cost, retry/deduplication and reply semantics only for an authorized integration; no automatic mock task, endpoint deployment, queuing/drop policy or schedule is created by reading this file.

Keep credential values out of source and logs. The old channel ID, channel secret, access-token and webhook-URL checklist identifies configuration categories only, not permission to retrieve or provision them. Privacy, rights and the affected return destination stay purpose-bound.

This maintenance did not call LINE, configure a webhook, send a message, create a queue or verify real authentication/delivery.

## Source uptake and recovery

Selectively adopts the purpose/authority distinctions in [the existing #324 source](https://github.com/chenchienheng/DCP-Pole-Projection/blob/00999341ff600a65ab3de641e4ce5615d6e9690d/04_adapter-layer/line_entry_chain_spec.md), blob `cdd2c093baabc08d9a7fee4613fa9d5a73733527`. It is not an exact whole-file import or whole-source acceptance. The complete predecessor remains at [the fixed parent](https://github.com/chenchienheng/DCP-Pole-Projection/blob/08eddfc06cbea9f6884200a247b21df83d8e39c3/04_adapter-layer/line_entry_chain_spec.md); restore only after checking newer changes.

These references do not install tools, grant access, change a live service, or authorize publication, merge, deletion or deployment. [Directory entry](README.md) and the [existing register](../CAPABILITY_ABSORPTION_REGISTER.md) retain the scope; source-era successor arrows are not a compulsory runtime pipeline.
