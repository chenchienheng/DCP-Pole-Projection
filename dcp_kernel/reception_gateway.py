from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import Decision


class GatewayDisposition(str, Enum):
    ROUTE = "ROUTE"
    OBSERVE_ONLY = "OBSERVE_ONLY"
    HOLD_SCOPE_IDENTITY_RIGHTS = "HOLD_SCOPE_IDENTITY_RIGHTS"
    HOLD_NO_RECEIVER = "HOLD_NO_RECEIVER"
    ESCALATE_OWNER_DECISION = "ESCALATE_OWNER_DECISION"


@dataclass(frozen=True)
class GatewayInput:
    request_id: str
    source_identified: bool
    scope_bounded: bool
    rights_valid: bool
    material_event: bool
    affected_receivers: tuple[str, ...]
    irreversible: bool = False
    sensitive: bool = False
    authority_change_requested: bool = False
    owner_decision_required: bool = False


@dataclass(frozen=True)
class GatewayAssessment:
    decision: Decision
    disposition: GatewayDisposition
    routed_receivers: tuple[str, ...]
    escalate_to_owner: bool
    reasons: tuple[str, ...]


def assess_gateway_request(item: GatewayInput) -> GatewayAssessment:
    if not item.source_identified or not item.scope_bounded or not item.rights_valid:
        return GatewayAssessment(
            Decision.HOLD,
            GatewayDisposition.HOLD_SCOPE_IDENTITY_RIGHTS,
            (),
            False,
            ("EXTERNAL_REQUEST_REQUIRES_SOURCE_SCOPE_AND_RIGHTS_CHECK",),
        )

    if not item.material_event:
        return GatewayAssessment(
            Decision.PASS,
            GatewayDisposition.OBSERVE_ONLY,
            (),
            False,
            ("NON_MATERIAL_REQUEST_DOES_NOT_WAKE_NATIVE_RECEIVERS",),
        )

    if not item.affected_receivers:
        return GatewayAssessment(
            Decision.HOLD,
            GatewayDisposition.HOLD_NO_RECEIVER,
            (),
            False,
            ("MATERIAL_REQUEST_WITHOUT_AFFECTED_RECEIVER_CANNOT_ROUTE",),
        )

    needs_owner = any(
        (
            item.irreversible,
            item.sensitive,
            item.authority_change_requested,
            item.owner_decision_required,
        )
    )
    if needs_owner:
        return GatewayAssessment(
            Decision.HOLD,
            GatewayDisposition.ESCALATE_OWNER_DECISION,
            item.affected_receivers,
            True,
            ("ONLY_OWNER_DECISION_IRREVERSIBLE_SENSITIVE_OR_AUTHORITY_CHANGE_ESCALATES",),
        )

    return GatewayAssessment(
        Decision.PASS,
        GatewayDisposition.ROUTE,
        item.affected_receivers,
        False,
        ("BOUNDED_REQUEST_ROUTED_WITHOUT_HUMAN_API_GATEWAY",),
    )
