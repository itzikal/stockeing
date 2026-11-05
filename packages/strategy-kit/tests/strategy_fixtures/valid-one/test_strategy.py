from pathlib import Path

from strategy_kit.discovery import list_strategies


def test_valid_one_is_listed() -> None:
    ids = [s.id for s in list_strategies(Path(__file__).parent.parent).strategies]
    assert "valid-one" in ids
