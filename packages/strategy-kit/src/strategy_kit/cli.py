"""Command-line entry point: `uv run strategy-kit <command>`."""

import argparse
from pathlib import Path

from strategy_kit.check import check_strategy
from strategy_kit.discovery import list_strategies


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="strategy-kit")
    commands = parser.add_subparsers(dest="command", required=True)
    list_cmd = commands.add_parser("list", help="List strategies and any load errors")
    list_cmd.add_argument("--dir", type=Path, default=None, help=_DIR_HELP)
    check_cmd = commands.add_parser("check", help="Run one strategy twice on fixture data")
    check_cmd.add_argument("strategy_id")
    check_cmd.add_argument("--dir", type=Path, default=None, help=_DIR_HELP)
    args = parser.parse_args(argv)
    if args.command == "check":
        return _check(args.strategy_id, args.dir)
    return _list(args.dir)


_DIR_HELP = "Strategies folder (default: strategies/ at the repo root)"


def _list(strategies_dir: Path | None) -> int:
    result = list_strategies(strategies_dir)
    for strategy in result.strategies:
        print(f"{strategy.id}  {strategy.name}  v{strategy.version}  {strategy.timeframe}")
    for error in result.errors:
        print(f"ERROR {error.folder}: {error.message}")
    if not result.strategies and not result.errors:
        print("No strategies found.")
    return 1 if result.errors else 0


def _check(strategy_id: str, strategies_dir: Path | None) -> int:
    result = check_strategy(strategy_id, strategies_dir)
    if result.passed:
        print(f"PASS {strategy_id}")
        return 0
    print(f"FAIL {strategy_id}")
    for problem in result.problems:
        print(f"  - {problem}")
    return 1
