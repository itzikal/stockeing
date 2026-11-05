from datetime import UTC, datetime
from typing import ClassVar

import pytest
from pydantic import BaseModel
from strategy_kit.contract import Strategy
from strategy_kit.fixtures import FixtureBreakout, FixtureParams, fixture_view
from strategy_kit.models import Decision, Position


class MissingEvaluate(Strategy):
    id: ClassVar[str] = "missing"
    name: ClassVar[str] = "Missing"
    version: ClassVar[str] = "1"
    timeframe: ClassVar[str] = "1d"
    Params: ClassVar[type[BaseModel]] = FixtureParams

    def scan(self, view, params):  # type: ignore[no-untyped-def]
        return []


def test_subclass_missing_evaluate_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        MissingEvaluate()  # type: ignore[abstract]


def test_view_never_returns_bars_after_as_of() -> None:
    as_of = datetime(2026, 1, 10, tzinfo=UTC)
    view = fixture_view(as_of)
    bars = view.bars("RISE", "1d", 100)
    assert len(bars) == 10
    assert bars["time"].max() <= as_of


def test_fixture_strategy_returns_valid_hits_and_decisions() -> None:
    strategy = FixtureBreakout()
    params = FixtureParams(lookback=20)
    view = fixture_view()

    hits = strategy.scan(view, params)
    assert [hit.symbol for hit in hits] == ["RISE"]

    decision = strategy.evaluate(view, "RISE", None, params)
    assert isinstance(decision, Decision)
    assert decision.action == "enter"
    assert decision.side == "long"

    flat = strategy.evaluate(view, "FLAT", None, params)
    assert flat.action == "hold"


def test_fixture_strategy_exits_on_stop_and_target() -> None:
    strategy = FixtureBreakout()
    params = FixtureParams(lookback=20)
    view = fixture_view()
    entry = strategy.evaluate(view, "RISE", None, params)
    assert entry.entry is not None and entry.stop is not None and entry.target is not None
    position = Position(
        side="long",
        entry=entry.entry,
        quantity=10,
        stop=entry.stop,
        target=entry.target,
        entry_time=view.as_of,
    )
    held = strategy.evaluate(view, "RISE", position, params)
    assert held.action == "hold"
    stopped = position.model_copy(update={"stop": entry.entry + 1})
    assert strategy.evaluate(view, "RISE", stopped, params).reason == "stop hit"
