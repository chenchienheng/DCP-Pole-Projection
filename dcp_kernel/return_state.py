from __future__ import annotations

from dataclasses import dataclass, replace

from .models import ReturnState


class IllegalReturnTransition(ValueError):
    pass


_RETURN_ORDER = tuple(ReturnState)


@dataclass(frozen=True)
class ReturnClosure:
    return_id: str
    receiver: str
    state: ReturnState = ReturnState.PRODUCED
    receiver_actual_read: bool = False
    native_disposition: str | None = None
    rebuild_applied: bool = False
    no_rebuild_reason: str | None = None
    behavior_delta_observed: bool = False
    retested: bool = False
    manual_interventions: tuple[str, ...] = ()

    def advance(self, target: ReturnState, **updates: object) -> "ReturnClosure":
        current_index = _RETURN_ORDER.index(self.state)
        target_index = _RETURN_ORDER.index(target)
        if target_index != current_index + 1:
            raise IllegalReturnTransition(
                f"illegal return transition: {self.state.value} -> {target.value}"
            )

        candidate = replace(self, state=target, **updates)
        candidate._validate_target()
        return candidate

    def _validate_target(self) -> None:
        if self.state is ReturnState.ACTUAL_READ and not self.receiver_actual_read:
            raise IllegalReturnTransition("ACTUAL_READ requires receiver evidence")
        if (
            self.state is ReturnState.RECEIVER_NATIVE_DISPOSITION
            and not self.native_disposition
        ):
            raise IllegalReturnTransition(
                "RECEIVER_NATIVE_DISPOSITION requires receiver-owned disposition"
            )
        if self.state is ReturnState.REBUILD_APPLIED_OR_NO_REBUILD_WITH_REASON:
            if not self.rebuild_applied and not self.no_rebuild_reason:
                raise IllegalReturnTransition(
                    "rebuild state requires applied rebuild or explicit no-rebuild reason"
                )
        if (
            self.state is ReturnState.BEHAVIOR_DELTA_OBSERVED
            and not self.behavior_delta_observed
        ):
            raise IllegalReturnTransition(
                "BEHAVIOR_DELTA_OBSERVED requires behavior evidence"
            )
        if self.state is ReturnState.RETESTED and not self.retested:
            raise IllegalReturnTransition("RETESTED requires retest evidence")

    @property
    def outstanding_debt(self) -> tuple[str, ...]:
        debts: list[str] = []
        if _RETURN_ORDER.index(self.state) < _RETURN_ORDER.index(ReturnState.ACTUAL_READ):
            debts.append("READ_DEBT")
        if _RETURN_ORDER.index(self.state) < _RETURN_ORDER.index(
            ReturnState.RECEIVER_NATIVE_DISPOSITION
        ):
            debts.append("NATIVE_DISPOSITION_DEBT")
        if _RETURN_ORDER.index(self.state) < _RETURN_ORDER.index(ReturnState.RECONCILED):
            debts.append("RECONCILIATION_DEBT")
        if _RETURN_ORDER.index(self.state) < _RETURN_ORDER.index(
            ReturnState.REBUILD_APPLIED_OR_NO_REBUILD_WITH_REASON
        ):
            debts.append("REBUILD_DEBT")
        if _RETURN_ORDER.index(self.state) < _RETURN_ORDER.index(
            ReturnState.BEHAVIOR_DELTA_OBSERVED
        ):
            debts.append("BEHAVIOR_DELTA_DEBT")
        if _RETURN_ORDER.index(self.state) < _RETURN_ORDER.index(ReturnState.RETESTED):
            debts.append("RETEST_DEBT")
        return tuple(debts)

    @property
    def autonomy_level(self) -> str:
        if self.manual_interventions:
            return "A0_MANUAL_PROMPT_DEPENDENT"
        if self.state is ReturnState.RETESTED:
            return "A4_RETESTED"
        if self.state is ReturnState.BEHAVIOR_DELTA_OBSERVED:
            return "A3_BEHAVIOR_CHANGED"
        if _RETURN_ORDER.index(self.state) >= _RETURN_ORDER.index(
            ReturnState.RECEIVER_NATIVE_DISPOSITION
        ):
            return "A2_ABSORBED"
        if _RETURN_ORDER.index(self.state) >= _RETURN_ORDER.index(ReturnState.ROUTED):
            return "A1_ROUTED"
        return "A0_MANUAL_PROMPT_DEPENDENT"
