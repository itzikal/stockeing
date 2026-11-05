# Strategy rules

How to add a trading strategy to this repo. Follow it from a plain-language description to a strategy that passes `strategy-kit check`.

## Folder layout

```
strategies/<strategy-id>/strategy.py        Rules and parameters (one Strategy subclass)
strategies/<strategy-id>/test_strategy.py   Tests for that strategy
```

- `<strategy-id>` is kebab-case, for example `breakout-20d`. It must match the `id` attribute exactly.
- Change nothing outside `strategies/<strategy-id>/`. A new strategy needs no registration, install, or edits to other files.

## The contract

Copy this shape. The authoritative definitions are in `packages/strategy-kit/src/strategy_kit/contract.py` and `models.py`.

```python
from typing import ClassVar

from pydantic import BaseModel, Field

from strategy_kit.contract import MarketView, Strategy
from strategy_kit.models import Decision, Position, ScanHit


class Params(BaseModel):
    lookback: int = Field(20, ge=5, le=200, description="Days for the breakout high")


class Breakout20D(Strategy):
    id: ClassVar[str] = "breakout-20d"        # Must match the folder name
    name: ClassVar[str] = "20-day breakout"
    version: ClassVar[str] = "1"              # Bump when the rules change
    timeframe: ClassVar[str] = "1d"           # For example "1d" or "5m"
    Params: ClassVar[type[BaseModel]] = Params

    def scan(self, view: MarketView, params: BaseModel) -> list[ScanHit]:
        ...

    def evaluate(
        self, view: MarketView, symbol: str, position: Position | None, params: BaseModel
    ) -> Decision:
        ...
```

- `scan` returns the symbols worth a closer look. Higher `score` ranks first. Each hit needs a `reason`.
- `evaluate` returns one `Decision` for a symbol. `position` is `None` when nothing is open, or the open `Position` when one is.
- `Decision.action` is `enter`, `exit`, or `hold`. The UI shows them as buy, sell, and hold.
- `enter` needs `side`, `entry`, `stop`, and `target`. For `long`, `stop < entry < target`. For `short`, `target < entry < stop`.
- Every decision needs a non-empty `reason`, including `hold`. The journal records every decision.
- `exit` and `hold` need no prices. A strategy decides its own exits in `evaluate`. Stop and target fills are handled by whichever module runs it.
- Strategies decide only *what* to do. Fees, position sizing, and account limits belong to `backtester`, not to a strategy.

## Rules

1. **Market data only through `view`.** Use `view.symbols()` and `view.bars(symbol, timeframe, count)`. Make no network calls and no file reads.
2. **Only use data up to `view.as_of`.** The view already enforces this. Do not work around it, for example by reading the clock or loading a file of prices.
3. **Stay deterministic.** Do not read the clock (`datetime.now`, `time.time`). Do not use unseeded randomness. The same inputs must always give the same decisions.
4. **Put every adjustable value in `Params`.** Each field needs bounds (`ge`, `le`) and a `description`. Do not hard-code numbers that a user might want to tune.
5. **Change `version` when the rules change.** Old test results must stay traceable to the rules that produced them.
6. **Write tests.** Put them in `test_strategy.py` in the strategy folder. Test at least one case where it enters, one where it holds, and one where it exits. Use this pattern to get the strategy in a test:

   ```python
   from pathlib import Path

   from strategy_kit.discovery import StrategyInfo, list_strategies
   from strategy_kit.fixtures import fixture_view


   def load() -> StrategyInfo:
       found = list_strategies(Path(__file__).parent.parent).strategies
       return next(s for s in found if s.id == "breakout-20d")


   def test_enters_on_breakout() -> None:
       info = load()
       params = info.cls.Params(lookback=20)
       decision = info.cls().evaluate(fixture_view(), "RISE", None, params)
       assert decision.action == "enter"
   ```

   Use `fixture_view()` for data. Its symbols are `RISE` (closes above its prior high on the last bar) and `FLAT` (never breaks out).
7. **Pass the checks** before calling the strategy done.

## Steps

1. Restate the strategy's rules in plain words. Confirm the entry, the stop, the target, the exits, and the parameters with the owner. Write down anything left open rather than guessing.
2. Create `strategies/<strategy-id>/strategy.py` following the contract above.
3. Create `strategies/<strategy-id>/test_strategy.py` with the tests from rule 6.
4. Run the checks:

   ```
   uv run pytest strategies/<strategy-id>
   uv run strategy-kit check <strategy-id>
   uv run strategy-kit list
   uv run ruff check strategies/<strategy-id>
   uv run mypy strategies/<strategy-id>/strategy.py
   ```

   `strategy-kit check` runs the strategy twice on fixture data. It fails if the strategy does not load, returns an invalid decision, raises, or gives different results on the two runs.
5. If a check fails, fix the strategy and rerun. `uv run ruff check strategies/<strategy-id> --fix` sorts imports and fixes simple lint problems. Do not weaken the rules or tests to get a pass.

## Limits of the checks

Strategies are local code run with full permissions. These rules are conventions, not a security sandbox. `strategy-kit check` runs only fixture data, so a strategy that behaves differently on some real dates can still pass. Review the rules and the tests yourself.

## Not in this module

Real market data, fees, sizing, account limits, broker calls, and Pine Script output belong to other modules: `research`, `backtester`, and `pine-bridge`. Keep them out of strategy code.
