# Tasks: strategy-kit

Spec: `SPEC-strategy-kit.md`. Plan: `tasks/plan.md`.

## Phase 1: Foundation

### Task 1: Set up the workspace and tooling

Create the root `uv` workspace and an empty `strategy-kit` package, with pytest, ruff, and mypy configured. Add a `.gitignore` covering `.vs/`, `graphify-out/`, and Python build and cache files.

**Acceptance criteria:**
- [x] `uv sync` installs the workspace on Python 3.13
- [x] `.vs/` no longer shows in `git status`

**Verification:**
- [x] `uv run pytest packages/strategy-kit` passes with one smoke test
- [x] `uv run ruff check .` and `uv run mypy packages/strategy-kit` pass

**Dependencies:** None

**Files likely touched:** `pyproject.toml`, `.gitignore`, `packages/strategy-kit/pyproject.toml`, `packages/strategy-kit/src/strategy_kit/__init__.py`, `packages/strategy-kit/tests/test_smoke.py`

**Estimated scope:** Medium

### Task 2: Add decision models with validation

Add `ScanHit`, `Decision`, and `Position`, with the spec's validation rules.

**Acceptance criteria:**
- [ ] `enter` without a side, entry, stop, or target is rejected
- [ ] Prices in the wrong order are rejected for long and for short (success criterion 4)
- [ ] An empty `reason` is rejected for every action

**Verification:**
- [ ] `uv run pytest packages/strategy-kit -k models` passes

**Dependencies:** Task 1

**Files likely touched:** `packages/strategy-kit/src/strategy_kit/models.py`, `packages/strategy-kit/tests/test_models.py`

**Estimated scope:** Small

### Task 3: Add the strategy contract and test fixtures

Add `MarketView` and the `Strategy` base class, plus an in-memory fixture view and a valid fixture strategy that later tasks and `strategy-kit check` run against.

**Acceptance criteria:**
- [ ] A subclass missing `scan` or `evaluate` can't be instantiated
- [ ] The fixture view never returns bars after its `as_of` time
- [ ] The fixture strategy returns valid hits and decisions from the fixture view

**Verification:**
- [ ] `uv run pytest packages/strategy-kit -k contract` passes
- [ ] `uv run mypy packages/strategy-kit` passes on the fixture strategy

**Dependencies:** Task 2

**Files likely touched:** `packages/strategy-kit/src/strategy_kit/contract.py`, `packages/strategy-kit/src/strategy_kit/fixtures.py`, `packages/strategy-kit/tests/test_contract.py`

**Estimated scope:** Medium

## Checkpoint: Foundation

- [ ] Tests, ruff, and mypy pass

## Phase 2: Discovery and check

### Task 4: Discover strategies

Add `list_strategies()`, which loads each `strategies/<id>/strategy.py` by file path and returns its metadata and parameter JSON Schema, plus any load errors.

**Acceptance criteria:**
- [ ] A valid strategy is returned with a valid JSON Schema (success criterion 2)
- [ ] A broken file, two classes in one file, or an id that doesn't match its folder is reported as an error, and the others still load (success criterion 3)
- [ ] Two strategies with a `test_strategy.py` both run under pytest

**Verification:**
- [ ] `uv run pytest packages/strategy-kit -k discovery` passes

**Dependencies:** Task 3

**Files likely touched:** `packages/strategy-kit/src/strategy_kit/discovery.py`, `packages/strategy-kit/tests/test_discovery.py`, fixture folders in `packages/strategy-kit/tests/`

**Estimated scope:** Medium

### Task 5: Add the `list` command

Add `uv run strategy-kit list`, which prints each strategy and any load errors.

**Acceptance criteria:**
- [ ] A new `strategies/<id>/` folder appears with no changes outside that folder (success criterion 1)
- [ ] The command exits non-zero if any strategy failed to load

**Verification:**
- [ ] `uv run pytest packages/strategy-kit -k cli` passes
- [ ] Manual check: `uv run strategy-kit list` shows a temporary strategy folder, and stops showing it once removed

**Dependencies:** Task 4

**Files likely touched:** `packages/strategy-kit/src/strategy_kit/cli.py`, `packages/strategy-kit/pyproject.toml`, `packages/strategy-kit/tests/test_cli.py`

**Estimated scope:** Small

### Task 6: Add the `check` command

Add `uv run strategy-kit check <strategy-id>`, which runs a strategy twice against fixture data.

**Acceptance criteria:**
- [ ] A valid strategy passes (success criterion 5)
- [ ] A strategy using unseeded randomness fails, and the message says the runs differed (success criterion 5)
- [ ] A strategy that fails to load or returns an invalid decision fails, with the reason

**Verification:**
- [ ] `uv run pytest packages/strategy-kit -k check` passes

**Dependencies:** Task 5

**Files likely touched:** `packages/strategy-kit/src/strategy_kit/check.py`, `packages/strategy-kit/src/strategy_kit/cli.py`, `packages/strategy-kit/tests/test_check.py`

**Estimated scope:** Small

## Checkpoint: Discovery and check

- [ ] Success criteria 1 to 5 from the spec pass
- [ ] Tests, ruff, and mypy pass

## Phase 3: Strategy authoring

### Task 7: Write the strategy rules

Write `docs/strategy-rules.md`, and update `CLAUDE.md` with the real commands and a pointer to the rules.

**Acceptance criteria:**
- [ ] The doc covers the folder layout, the contract, every rule in the spec, and the steps to finish a strategy
- [ ] Every command in `CLAUDE.md` has been run and works

**Verification:**
- [ ] Manual check: run each documented command

**Dependencies:** Task 6

**Files likely touched:** `docs/strategy-rules.md`, `CLAUDE.md`

**Estimated scope:** Small

### Task 8: Trial the rules with a fresh agent

Give a fresh agent a plain-language strategy description and only the repo. Fix any gaps it hits in the rules, then delete the trial strategy, since real strategies come after `research`.

**Acceptance criteria:**
- [ ] The agent's strategy passes `strategy-kit check` and appears in `strategy-kit list` (success criterion 6)
- [ ] The agent changed nothing outside its strategy folder
- [ ] The trial strategy is removed afterwards

**Verification:**
- [ ] `uv run strategy-kit check <trial-id>` passes before removal
- [ ] `git status` shows no leftover trial files

**Dependencies:** Task 7

**Files likely touched:** `docs/strategy-rules.md`, a temporary folder in `strategies/`

**Estimated scope:** Small

## Checkpoint: Complete

- [ ] All 7 success criteria from the spec pass
- [ ] Reviewed with the owner
