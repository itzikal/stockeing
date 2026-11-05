import shutil
from pathlib import Path

import pytest
from strategy_kit.cli import main

FIXTURES = Path(__file__).parent / "strategy_fixtures"


def test_cli_list_shows_each_strategy_and_exits_zero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["list", "--dir", str(FIXTURES)]) == 0
    out = capsys.readouterr().out
    assert "valid-one" in out
    assert "valid-two" in out
    assert "ERROR" not in out


def test_cli_list_exits_nonzero_when_a_strategy_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    shutil.copytree(FIXTURES / "valid-one", tmp_path / "valid-one")
    (tmp_path / "broken").mkdir()
    (tmp_path / "broken" / "strategy.py").write_text("def broken(:\n", encoding="utf-8")

    assert main(["list", "--dir", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "valid-one" in out
    assert "ERROR broken: SyntaxError" in out


def test_new_strategy_folder_appears_then_disappears(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["list", "--dir", str(tmp_path)]) == 0
    assert "No strategies found." in capsys.readouterr().out

    folder = tmp_path / "valid-one"
    shutil.copytree(FIXTURES / "valid-one", folder)
    assert main(["list", "--dir", str(tmp_path)]) == 0
    assert "valid-one" in capsys.readouterr().out

    shutil.rmtree(folder)
    assert main(["list", "--dir", str(tmp_path)]) == 0
    assert "valid-one" not in capsys.readouterr().out
