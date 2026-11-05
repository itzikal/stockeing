"""Find strategies under `strategies/` and load each one from its file path."""

import importlib.util
import inspect
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from strategy_kit.contract import Strategy

STRATEGY_FILE = "strategy.py"


@dataclass(frozen=True)
class StrategyInfo:
    id: str
    name: str
    version: str
    timeframe: str
    params_schema: dict[str, Any]
    cls: type[Strategy]


@dataclass(frozen=True)
class LoadError:
    folder: str
    message: str


@dataclass
class Discovery:
    strategies: list[StrategyInfo] = field(default_factory=list)
    errors: list[LoadError] = field(default_factory=list)


def find_repo_root(start: Path | None = None) -> Path:
    """Nearest folder at or above `start` whose pyproject.toml declares the uv workspace."""
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        pyproject = candidate / "pyproject.toml"
        if pyproject.is_file():
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            if "workspace" in data.get("tool", {}).get("uv", {}):
                return candidate
    return here


def list_strategies(strategies_dir: Path | None = None) -> Discovery:
    root = strategies_dir or find_repo_root() / "strategies"
    result = Discovery()
    if not root.is_dir():
        return result
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        source = folder / STRATEGY_FILE
        if not source.is_file():
            continue
        try:
            result.strategies.append(_load(folder.name, source))
        except Exception as exc:  # noqa: BLE001 - one broken strategy must not stop the others
            result.errors.append(LoadError(folder.name, f"{type(exc).__name__}: {exc}"))
    return result


def _load(folder_name: str, source: Path) -> StrategyInfo:
    module_name = "strategy_" + re.sub(r"\W", "_", folder_name)
    spec = importlib.util.spec_from_file_location(module_name, source)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot read {source}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise

    classes = [
        obj
        for obj in vars(module).values()
        if inspect.isclass(obj)
        and issubclass(obj, Strategy)
        and obj is not Strategy
        and obj.__module__ == module_name
    ]
    if len(classes) != 1:
        raise ValueError(f"expected exactly one Strategy subclass, found {len(classes)}")
    cls = classes[0]
    if inspect.isabstract(cls):
        raise ValueError(f"{cls.__name__} must implement scan and evaluate")
    for attr in ("id", "name", "version", "timeframe"):
        value = getattr(cls, attr, None)
        if not isinstance(value, str) or not value:
            raise ValueError(f"{cls.__name__} must set {attr}")
    if cls.id != folder_name:
        raise ValueError(f"id '{cls.id}' must match folder name '{folder_name}'")
    params = getattr(cls, "Params", None)
    if not (inspect.isclass(params) and issubclass(params, BaseModel)):
        raise ValueError("Params must be a pydantic BaseModel subclass")
    return StrategyInfo(
        id=cls.id,
        name=cls.name,
        version=cls.version,
        timeframe=cls.timeframe,
        params_schema=params.model_json_schema(),
        cls=cls,
    )
