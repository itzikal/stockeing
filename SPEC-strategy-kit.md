# Spec: strategy-kit

Status: approved 2026-11-05.

## Objective

Define what a strategy is, so that a strategy Claude Code writes from a plain-language description runs in `research`, `trade`, and `backtester`, and appears in `web` with a parameter form, with no changes to those modules.

The user is the repo owner, working through Claude Code.

## Tech stack

- Python 3.13, in a `uv` workspace
- Pydantic v2 for decisions and parameters. Its JSON Schema output is what `web` will build parameter forms from
- pandas, for the bars `MarketView` returns
- pytest, ruff, and mypy

## Commands

These become valid once the first implementation task is done.

```
Install:         uv sync
Test module:     uv run pytest packages/strategy-kit
Single test:     uv run pytest packages/strategy-kit -k <name>
Lint:            uv run ruff check .
Types:           uv run mypy packages/strategy-kit
List strategies: uv run strategy-kit list
Check one:       uv run strategy-kit check <strategy-id>
```

## Project structure

```
packages/strategy-kit/src/strategy_kit/   Contract, discovery, and check command
packages/strategy-kit/tests/              Kit tests, including a fixture strategy
strategies/<strategy-id>/strategy.py      One strategy: rules and parameters
strategies/<strategy-id>/test_strategy.py Tests for that strategy
strategies/<strategy-id>/strategy.pine    Added later, by pine-bridge
docs/strategy-rules.md                    Rules Claude Code follows to add a strategy
```

## The contract

`MarketView` is defined here and implemented by `research`, so that this module depends on nothing. It only returns data up to its as-of time.

```python
class MarketView(Protocol):
    as_of: datetime
    def symbols(self) -> list[str]: ...
    def bars(self, symbol: str, timeframe: str, count: int) -> pd.DataFrame: ...


class Params(BaseModel):
    lookback: int = Field(20, ge=5, le=200, description="Days for the breakout high")


class ScanHit(BaseModel):
    symbol: str
    score: float  # Higher ranks first
    reason: str


class Decision(BaseModel):
    action: Literal["enter", "exit", "hold"]  # Shown in the UI as buy, sell, or hold
    side: Literal["long", "short"] | None = None  # Required for enter
    entry: Decimal | None = None
    stop: Decimal | None = None
    target: Decimal | None = None
    reason: str  # Required for every action, because journal records them all


class Strategy(ABC):
    id: ClassVar[str]         # Must match the folder name
    name: ClassVar[str]
    version: ClassVar[str]    # Change it when the rules change, so old test results stay traceable
    timeframe: ClassVar[str]  # For example "1d" or "5m"
    Params: ClassVar[type[BaseModel]]

    @abstractmethod
    def scan(self, view: MarketView, params: BaseModel) -> list[ScanHit]: ...

    @abstractmethod
    def evaluate(
        self, view: MarketView, symbol: str, position: Position | None, params: BaseModel
    ) -> Decision: ...
```

`Position` holds the open side, entry price, quantity, stop, target, and entry time. A strategy decides its own exits in `evaluate`, and stop and target fills are handled by whichever module runs it.

Validation on `Decision`:

- `enter` needs a side, entry, stop, and target.
- For long, stop < entry < target. For short, target < entry < stop.
- `reason` can't be empty.

Fees, position sizing, and account limits don't belong in a strategy. `backtester` applies them.

## Discovery

- A strategy is any `strategies/<strategy-id>/strategy.py` that defines exactly one `Strategy` subclass.
- `list_strategies()` returns each strategy's id, name, version, timeframe, and parameter JSON Schema.
- A broken strategy is reported with its error, and doesn't stop the others from loading.

## Rules for strategies

`docs/strategy-rules.md` tells Claude Code to:

- Use only `MarketView` for market data, with no network or file access.
- Stay deterministic: no clock reads and no unseeded randomness, so the same inputs always give the same decisions.
- Put every adjustable value in `Params`, with bounds and a description.
- Write tests, and pass `strategy-kit check <strategy-id>` before calling the strategy done.

`strategy-kit check` runs a strategy against fixture data. It fails if the strategy doesn't load, returns an invalid decision, or gives different results on two identical runs.

Strategies are local code run with full permissions, so these rules are conventions and aren't a security sandbox.

## Testing strategy

- Unit tests for `Decision` validation, on both long and short.
- Discovery tests using fixture strategies: valid, broken, two classes in one file, and an id that doesn't match its folder.
- Tests for `strategy-kit check`, including a strategy that uses randomness and must fail.
- No fixed coverage target.

## Boundaries

- **Always:** Change `version` when a strategy's rules change. Keep this module free of imports from other modules.
- **Ask first:** Changing the `Strategy` or `Decision` format once another module depends on it. Adding a dependency beyond those listed here.
- **Never:** Put fees, sizing, broker calls, or data fetching in this module or in a strategy.

## Success criteria

1. A new `strategies/<id>/` folder appears in `uv run strategy-kit list` with no changes outside that folder.
2. `list_strategies()` returns a valid JSON Schema for each strategy's parameters.
3. A broken strategy is reported with its error, and the others still load.
4. An `enter` decision with an invalid stop or target is rejected, on both long and short.
5. `strategy-kit check` fails a non-deterministic strategy and passes a valid one.
6. Following only `docs/strategy-rules.md`, Claude Code can add a strategy from a plain-language description that passes `strategy-kit check`.
7. Tests, ruff, and mypy all pass.

## Open questions

1. **Long, short, or both?** The format allows both, so this can wait until we define real strategies.
2. **Does this spec need a real strategy?** It assumes fixtures only, with the first real strategy defined after `research` exists.
3. **Should scaling in or out be possible?** This spec assumes not, so each position is entered and exited once. That keeps the first version simple, and suits a $1,000 account given the $2.50 minimum per order.
