# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current state

- The repository has no source code, build system, tests, or README yet. The only tracked commit is an empty initial commit.
- `.vs/` holds Visual Studio cache files. It is untracked and should not be committed. Add it to `.gitignore` before the first real commit.
- Remote: `origin` is `git@github.com:itzikal/stockeing.git`, branch `main`.

## Project documents

- `docs/intent/trading-system.md`: what we're building and why.
- `CAPABILITY-MAP.md`: modules, dependencies, and build order.
- `SPEC-<module-id>.md`: the spec for each module.

Update this file with build, lint, test, and architecture notes once code exists.
