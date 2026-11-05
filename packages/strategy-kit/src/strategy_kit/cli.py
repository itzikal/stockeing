"""Command-line entry point: `uv run strategy-kit <command>`."""

import argparse
from pathlib import Path

from strategy_kit.discovery import list_strategies


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="strategy-kit")
    commands = parser.add_subparsers(dest="command", required=True)
    list_cmd = commands.add_parser("list", help="List strategies and any load errors")
    list_cmd.add_argument(
        "--dir",
        type=Path,
        default=None,
        help="Strategies folder (default: strategies/ at the repo root)",
    )
    args = parser.parse_args(argv)
    return _list(args.dir)


def _list(strategies_dir: Path | None) -> int:
    result = list_strategies(strategies_dir)
    for strategy in result.strategies:
        print(f"{strategy.id}  {strategy.name}  v{strategy.version}  {strategy.timeframe}")
    for error in result.errors:
        print(f"ERROR {error.folder}: {error.message}")
    if not result.strategies and not result.errors:
        print("No strategies found.")
    return 1 if result.errors else 0
