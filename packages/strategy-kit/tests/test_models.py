from decimal import Decimal

import pytest
from pydantic import ValidationError
from strategy_kit.models import Decision


def enter(side: str, entry: str, stop: str, target: str, reason: str = "breakout") -> Decision:
    return Decision(
        action="enter",
        side=side,  # type: ignore[arg-type]
        entry=Decimal(entry),
        stop=Decimal(stop),
        target=Decimal(target),
        reason=reason,
    )


def test_valid_long_and_short_enter() -> None:
    assert enter("long", "10", "9", "12").side == "long"
    assert enter("short", "10", "11", "8").side == "short"


@pytest.mark.parametrize("missing", ["side", "entry", "stop", "target"])
def test_enter_requires_every_price_and_side(missing: str) -> None:
    fields: dict[str, object] = {
        "action": "enter",
        "side": "long",
        "entry": Decimal(10),
        "stop": Decimal(9),
        "target": Decimal(12),
        "reason": "x",
    }
    fields[missing] = None
    with pytest.raises(ValidationError, match=missing):
        Decision.model_validate(fields)


@pytest.mark.parametrize(
    ("side", "entry", "stop", "target"),
    [
        ("long", "10", "10", "12"),  # stop equal to entry
        ("long", "10", "9", "9"),  # target below entry
        ("long", "10", "11", "12"),  # stop above entry
        ("short", "10", "9", "8"),  # stop below entry
        ("short", "10", "11", "10"),  # target equal to entry
    ],
)
def test_wrong_price_order_is_rejected(side: str, entry: str, stop: str, target: str) -> None:
    with pytest.raises(ValidationError):
        enter(side, entry, stop, target)


@pytest.mark.parametrize("action", ["enter", "exit", "hold"])
def test_empty_reason_is_rejected_for_every_action(action: str) -> None:
    with pytest.raises(ValidationError, match="reason"):
        Decision(action=action, reason="   ")  # type: ignore[arg-type]


def test_exit_and_hold_need_no_prices() -> None:
    assert Decision(action="hold", reason="nothing yet").action == "hold"
    assert Decision(action="exit", reason="stop hit").action == "exit"
