"""In-memory market data and a small strategy for tests and `strategy-kit check`."""

from datetime import datetime
from decimal import Decimal
from typing import ClassVar

import pandas as pd
from pydantic import BaseModel, Field

from strategy_kit.contract import MarketView, Strategy
from strategy_kit.models import Decision, Position, ScanHit


class InMemoryView:
    def __init__(self, as_of: datetime, data: dict[tuple[str, str], pd.DataFrame]) -> None:
        self.as_of = as_of
        self._data = data

    def symbols(self) -> list[str]:
        return sorted({symbol for symbol, _ in self._data})

    def bars(self, symbol: str, timeframe: str, count: int) -> pd.DataFrame:
        frame = self._data[(symbol, timeframe)]
        visible = frame[frame["time"] <= self.as_of]
        return visible.tail(count).reset_index(drop=True)


def daily_bars(closes: list[float]) -> pd.DataFrame:
    """Bars whose high and low sit 0.5 around each close."""
    times = pd.date_range("2026-01-01", periods=len(closes), freq="D", tz="UTC")
    return pd.DataFrame(
        {
            "time": times,
            "open": closes,
            "high": [c + 0.5 for c in closes],
            "low": [c - 0.5 for c in closes],
            "close": closes,
            "volume": [1_000_000] * len(closes),
        }
    )


def fixture_view(as_of: datetime | None = None) -> InMemoryView:
    rising = [10.0 + i * 0.1 for i in range(25)] + [13.0]
    flat = [10.0] * 26
    data = {("RISE", "1d"): daily_bars(rising), ("FLAT", "1d"): daily_bars(flat)}
    if as_of is None:
        as_of = pd.Timestamp("2026-02-01", tz="UTC").to_pydatetime()
    return InMemoryView(as_of, data)


class FixtureParams(BaseModel):
    lookback: int = Field(20, ge=5, le=200, description="Days for the breakout high")


def _price(value: float) -> Decimal:
    return Decimal(str(round(value, 2)))


class FixtureBreakout(Strategy):
    id: ClassVar[str] = "fixture-breakout"
    name: ClassVar[str] = "Fixture breakout"
    version: ClassVar[str] = "1"
    timeframe: ClassVar[str] = "1d"
    Params: ClassVar[type[BaseModel]] = FixtureParams

    def scan(self, view: MarketView, params: BaseModel) -> list[ScanHit]:
        assert isinstance(params, FixtureParams)
        hits: list[ScanHit] = []
        for symbol in view.symbols():
            bars = view.bars(symbol, self.timeframe, params.lookback + 1)
            if len(bars) < params.lookback + 1:
                continue
            high = float(bars["high"].iloc[:-1].max())
            close = float(bars["close"].iloc[-1])
            if close > high:
                hits.append(
                    ScanHit(symbol=symbol, score=close / high, reason="closed above prior high")
                )
        return sorted(hits, key=lambda hit: hit.score, reverse=True)

    def evaluate(
        self, view: MarketView, symbol: str, position: Position | None, params: BaseModel
    ) -> Decision:
        assert isinstance(params, FixtureParams)
        bars = view.bars(symbol, self.timeframe, params.lookback + 1)
        close = float(bars["close"].iloc[-1])
        if position is not None:
            if close <= float(position.stop):
                return Decision(action="exit", reason="stop hit")
            if close >= float(position.target):
                return Decision(action="exit", reason="target hit")
            return Decision(action="hold", reason="inside stop and target")
        high = float(bars["high"].iloc[:-1].max())
        if close <= high:
            return Decision(action="hold", reason="no breakout")
        stop = float(bars["low"].iloc[:-1].min())
        entry = _price(close)
        return Decision(
            action="enter",
            side="long",
            entry=entry,
            stop=_price(stop),
            target=entry + (entry - _price(stop)) * 2,
            reason="closed above prior high",
        )
