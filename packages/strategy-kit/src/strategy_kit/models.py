"""Decision, scan-hit, and position models shared by every strategy."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, model_validator


class ScanHit(BaseModel):
    symbol: str
    score: float  # Higher ranks first
    reason: str


class Position(BaseModel):
    side: Literal["long", "short"]
    entry: Decimal
    quantity: int
    stop: Decimal
    target: Decimal
    entry_time: datetime


class Decision(BaseModel):
    action: Literal["enter", "exit", "hold"]  # Shown in the UI as buy, sell, or hold
    side: Literal["long", "short"] | None = None  # Required for enter
    entry: Decimal | None = None
    stop: Decimal | None = None
    target: Decimal | None = None
    reason: str  # Required for every action, because journal records them all

    @model_validator(mode="after")
    def _check(self) -> "Decision":
        if not self.reason.strip():
            raise ValueError("reason must not be empty")
        if self.action != "enter":
            return self
        missing = [
            name
            for name, value in (
                ("side", self.side),
                ("entry", self.entry),
                ("stop", self.stop),
                ("target", self.target),
            )
            if value is None
        ]
        if missing:
            raise ValueError(f"enter needs {', '.join(missing)}")
        assert self.entry is not None and self.stop is not None and self.target is not None
        if self.side == "long":
            ok = self.stop < self.entry < self.target
            order = "stop < entry < target"
        else:
            ok = self.target < self.entry < self.stop
            order = "target < entry < stop"
        if not ok:
            raise ValueError(f"{self.side} entry needs {order}")
        return self
