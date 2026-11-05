"""`strategy-kit check`: run a strategy twice on fixture data and validate what it returns."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

from strategy_kit.discovery import StrategyInfo, list_strategies
from strategy_kit.fixtures import fixture_view
from strategy_kit.models import Decision, ScanHit


@dataclass(frozen=True)
class CheckResult:
    passed: bool
    problems: list[str]


def check_strategy(strategy_id: str, strategies_dir: Path | None = None) -> CheckResult:
    discovery = list_strategies(strategies_dir)
    info = next((s for s in discovery.strategies if s.id == strategy_id), None)
    if info is None:
        problems = [e.message for e in discovery.errors if e.folder == strategy_id]
        return CheckResult(False, problems or [f"no strategy named '{strategy_id}'"])
    try:
        first_hits, first_decisions = _run(info)
        second_hits, second_decisions = _run(info)
    except Exception as exc:  # noqa: BLE001 - report whatever the strategy raised
        return CheckResult(False, [f"strategy raised {type(exc).__name__}: {exc}"])

    problems = _validate(first_hits, first_decisions)
    if _snapshot(first_hits, first_decisions) != _snapshot(second_hits, second_decisions):
        problems.append("two identical runs gave different results")
    return CheckResult(not problems, problems)


def _run(info: StrategyInfo) -> tuple[Any, list[tuple[str, Any]]]:
    strategy = info.cls()
    params = info.cls.Params()
    view = fixture_view()
    hits = strategy.scan(view, params)
    decisions = [
        (symbol, strategy.evaluate(view, symbol, None, params)) for symbol in view.symbols()
    ]
    return hits, decisions


def _dump(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_dump(item) for item in value]
    return value


def _snapshot(hits: Any, decisions: list[tuple[str, Any]]) -> str:
    payload = {"scan": _dump(hits), "decisions": [[s, _dump(d)] for s, d in decisions]}
    return json.dumps(payload, default=repr, sort_keys=True)


def _validate(hits: Any, decisions: list[tuple[str, Any]]) -> list[str]:
    if not isinstance(hits, list):
        return ["scan must return a list of ScanHit"]
    problems: list[str] = []
    for hit in hits:
        try:
            ScanHit.model_validate(_dump(hit))
        except ValidationError as exc:
            problems.append(f"invalid scan hit: {exc.errors()[0]['msg']}")
    for symbol, decision in decisions:
        try:
            Decision.model_validate(_dump(decision))
        except ValidationError as exc:
            problems.append(f"invalid decision for {symbol}: {exc.errors()[0]['msg']}")
    return problems
