from pathlib import Path

from strategy_kit.check import check_strategy

FIXTURES = Path(__file__).parent / "strategy_fixtures"

TEMPLATE = '''
import random
from decimal import Decimal
from typing import ClassVar

from pydantic import BaseModel

from strategy_kit.contract import MarketView, Strategy
from strategy_kit.models import Decision, Position, ScanHit


class P(BaseModel):
    pass


class Under(Strategy):
    id: ClassVar[str] = "{folder}"
    name: ClassVar[str] = "Test"
    version: ClassVar[str] = "1"
    timeframe: ClassVar[str] = "1d"
    Params: ClassVar[type[BaseModel]] = P

    def scan(self, view: MarketView, params: BaseModel) -> list[ScanHit]:
        {scan}

    def evaluate(
        self, view: MarketView, symbol: str, position: Position | None, params: BaseModel
    ) -> Decision:
        {evaluate}
'''

HOLD = 'return Decision(action="hold", reason="ok")'


def _make(root: Path, folder: str, scan: str = "return []", evaluate: str = HOLD) -> None:
    (root / folder).mkdir()
    source = TEMPLATE.format(folder=folder, scan=scan, evaluate=evaluate)
    (root / folder / "strategy.py").write_text(source, encoding="utf-8")


def test_valid_strategy_passes() -> None:
    result = check_strategy("valid-one", FIXTURES)
    assert result.passed, result.problems


def test_unseeded_randomness_fails_and_says_runs_differed(tmp_path: Path) -> None:
    _make(tmp_path, "random-one", scan="return [ScanHit(symbol='FLAT', score=random.random(), reason='r')]")
    result = check_strategy("random-one", tmp_path)
    assert not result.passed
    assert "two identical runs gave different results" in result.problems


def test_invalid_decision_fails_with_reason(tmp_path: Path) -> None:
    bad = (
        "return Decision.model_construct(action='enter', side='long', entry=Decimal('10'), "
        "stop=Decimal('11'), target=Decimal('12'), reason='x')"
    )
    _make(tmp_path, "bad-prices", evaluate=bad)
    result = check_strategy("bad-prices", tmp_path)
    assert not result.passed
    assert any("invalid decision for RISE" in p for p in result.problems)


def test_strategy_that_raises_fails_with_reason(tmp_path: Path) -> None:
    _make(tmp_path, "raises", evaluate="raise RuntimeError('boom')")
    result = check_strategy("raises", tmp_path)
    assert not result.passed
    assert result.problems == ["strategy raised RuntimeError: boom"]


def test_strategy_that_fails_to_load_fails_with_reason(tmp_path: Path) -> None:
    (tmp_path / "broken").mkdir()
    (tmp_path / "broken" / "strategy.py").write_text("def broken(:\n", encoding="utf-8")
    result = check_strategy("broken", tmp_path)
    assert not result.passed
    assert "SyntaxError" in result.problems[0]


def test_unknown_strategy_fails(tmp_path: Path) -> None:
    result = check_strategy("nope", tmp_path)
    assert not result.passed
