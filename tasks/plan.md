# Implementation Plan: strategy-kit

## Overview

Build the first module from `CAPABILITY-MAP.md`, as specified in `SPEC-strategy-kit.md`: the strategy format, automatic discovery, the check command, and the rules Claude Code follows to add a strategy. This task also sets up the Python side of the monorepo. The task checklist is in `tasks/todo.md`.

## Architecture decisions

- **Root `uv` workspace.** Every later Python module joins as `packages/<module>`, so they share one lockfile and environment.
- **`src` layout.** Tests run against the installed package, not against files that happen to be on the path.
- **Strategies load by file path** using `importlib.util`. Folders in `strategies/` aren't packages, so adding a strategy needs no installation or registration.
- **pytest uses `--import-mode=importlib`.** Every strategy has a `test_strategy.py`, and the default import mode fails on duplicate test file names.
- **CLI uses `argparse`.** Two subcommands don't justify another dependency.
- **The strategies folder is a parameter of `list_strategies()`,** defaulting to `strategies/` at the repo root, so tests can use fixture folders.

## Dependency order

```
Workspace → Decision models → Strategy contract and fixtures → Discovery → CLI list
                                                                         → CLI check → Rules doc → Trial
```

## Task list

Details and acceptance criteria are in `tasks/todo.md`.

### Phase 1: Foundation
- [x] Task 1: Set up the workspace and tooling
- [x] Task 2: Add decision models with validation
- [x] Task 3: Add the strategy contract and test fixtures

### Checkpoint: Foundation
- [x] Tests, ruff, and mypy pass

### Phase 2: Discovery and check
- [x] Task 4: Discover strategies
- [ ] Task 5: Add the `list` command
- [ ] Task 6: Add the `check` command

### Checkpoint: Discovery and check
- [ ] Success criteria 1 to 5 from the spec pass

### Phase 3: Strategy authoring
- [ ] Task 7: Write the strategy rules
- [ ] Task 8: Trial the rules with a fresh agent

### Checkpoint: Complete
- [ ] All 7 success criteria from the spec pass
- [ ] Reviewed with the owner

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| The format doesn't fit `research`, `trade`, or `backtester`, and changing it later touches every strategy | High | Keep it small, and review it again when the `research` spec is written, before real strategies exist |
| The determinism check misses a strategy that behaves differently only on some dates or data | Medium | Treat the check as a basic safety net. The rules doc and code review cover the rest |
| Strategy tests collide on import because they share a file name | Low | Use `--import-mode=importlib`, and cover it with a test in Task 4 |
| The rules doc only works for an agent that already knows this conversation | Medium | Task 8 runs the trial with a fresh agent that has only the repo |

## Parallelization

None. Tasks form a single chain, and the module is small enough that parallel agents would add coordination without saving time.

## Open questions

None. The spec's open questions resolved on approval: fixture strategies only, one entry and one exit per position, and the format allows both long and short.
