import shutil
from pathlib import Path

from strategy_kit.discovery import list_strategies

FIXTURES = Path(__file__).parent / "strategy_fixtures"


def test_valid_strategies_load_with_json_schema() -> None:
    result = list_strategies(FIXTURES)
    assert result.errors == []
    assert sorted(s.id for s in result.strategies) == ["valid-one", "valid-two"]
    schema = result.strategies[0].params_schema
    assert schema["properties"]["lookback"]["minimum"] == 5
    assert schema["properties"]["lookback"]["maximum"] == 200
    assert schema["properties"]["lookback"]["description"] == "Days for the breakout high"


def _write(root: Path, folder: str, source: str) -> None:
    (root / folder).mkdir(parents=True)
    (root / folder / "strategy.py").write_text(source, encoding="utf-8")


def test_broken_strategies_are_reported_and_others_still_load(tmp_path: Path) -> None:
    shutil.copytree(FIXTURES / "valid-one", tmp_path / "valid-one")
    _write(tmp_path, "syntax-error", "def broken(:\n")
    good = (FIXTURES / "valid-one" / "strategy.py").read_text(encoding="utf-8")
    _write(tmp_path, "two-classes", good + "\n\nclass Extra(ValidOne):\n    pass\n")
    _write(tmp_path, "wrong-id", good.replace('"valid-one"', '"other-id"', 1))

    result = list_strategies(tmp_path)

    assert [s.id for s in result.strategies] == ["valid-one"]
    errors = {e.folder: e.message for e in result.errors}
    assert set(errors) == {"syntax-error", "two-classes", "wrong-id"}
    assert "SyntaxError" in errors["syntax-error"]
    assert "found 2" in errors["two-classes"]
    assert "must match folder name" in errors["wrong-id"]
