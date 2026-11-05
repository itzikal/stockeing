# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current state

- Built so far: `strategy-kit` (strategy format, discovery, `list` and `check` commands). Next module: `research`, once its spec is approved.
- `.vs/` holds Visual Studio cache files and is git-ignored. Don't commit it.
- Remote: `origin` is `git@github.com:itzikal/stockeing.git`, branch `main`. Commit per task on `main`.

## Commands

Run from the repo root. Python 3.13, managed by `uv`.

```
uv sync                                    Install the workspace
uv run pytest packages/strategy-kit        Test strategy-kit (add -k <name> for one test)
uv run pytest strategies/<id>              Test one strategy
uv run ruff check .                        Lint
uv run mypy packages/strategy-kit          Type-check strategy-kit
uv run strategy-kit list                   List strategies and any load errors
uv run strategy-kit check <id>             Run a strategy twice on fixture data
```

## Architecture

- `packages/<module>/`: one uv workspace member per module. `strategy-kit` is the first; later modules join the same workspace.
- `strategies/<id>/strategy.py`: one trading strategy. Each folder is discovered and loaded by file path, so adding one needs no registration.
- `docs/strategy-rules.md`: the rules for writing a strategy. Read it before adding or changing a strategy.

## Project documents

- `docs/intent/trading-system.md`: what we're building and why.
- `CAPABILITY-MAP.md`: modules, dependencies, and build order.
- `SPEC-<module-id>.md`: the spec for each module.
- `tasks/plan.md` and `tasks/todo.md`: the current implementation plan and task list.
