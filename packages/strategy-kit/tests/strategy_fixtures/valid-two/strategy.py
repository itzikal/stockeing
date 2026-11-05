from typing import ClassVar

from pydantic import BaseModel, Field
from strategy_kit.contract import MarketView, Strategy
from strategy_kit.models import Decision, Position, ScanHit


class ValidTwoParams(BaseModel):
    lookback: int = Field(20, ge=5, le=200, description="Days for the breakout high")


class ValidTwo(Strategy):
    id: ClassVar[str] = "valid-two"
    name: ClassVar[str] = "ValidTwo"
    version: ClassVar[str] = "1"
    timeframe: ClassVar[str] = "1d"
    Params: ClassVar[type[BaseModel]] = ValidTwoParams

    def scan(self, view: MarketView, params: BaseModel) -> list[ScanHit]:
        return []

    def evaluate(
        self, view: MarketView, symbol: str, position: Position | None, params: BaseModel
    ) -> Decision:
        return Decision(action="hold", reason="fixture strategy")
