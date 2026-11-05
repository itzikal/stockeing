"""The contract every strategy implements and every engine calls."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import ClassVar, Protocol

import pandas as pd
from pydantic import BaseModel

from strategy_kit.models import Decision, Position, ScanHit


class MarketView(Protocol):
    """Market data as it was at `as_of`. Implementations never return later bars."""

    as_of: datetime

    def symbols(self) -> list[str]: ...

    def bars(self, symbol: str, timeframe: str, count: int) -> pd.DataFrame: ...


class Strategy(ABC):
    id: ClassVar[str]  # Must match the folder name
    name: ClassVar[str]
    version: ClassVar[str]  # Change it when the rules change
    timeframe: ClassVar[str]  # For example "1d" or "5m"
    Params: ClassVar[type[BaseModel]]

    @abstractmethod
    def scan(self, view: MarketView, params: BaseModel) -> list[ScanHit]: ...

    @abstractmethod
    def evaluate(
        self, view: MarketView, symbol: str, position: Position | None, params: BaseModel
    ) -> Decision: ...
