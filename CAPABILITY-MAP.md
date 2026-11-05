# Capability Map: Trading System, Phase 1

Implements the intent in `docs/intent/trading-system.md`. Each module gets its own `SPEC-<module-id>.md` at the repo root. Module ids do not change.

| Module id | Responsibility | Depends on |
|---|---|---|
| `strategy-kit` | Strategy format, parameters, automatic discovery, and the rules Claude Code follows | none |
| `research` | Market data, news, technical signals, and a scanner that builds the watchlist | `strategy-kit` |
| `trade` | Evaluates the research and decides buy, sell, or hold, with entry, stop, target, and reason. Produces the live ranked list. Places no orders in Phase 1 | `research`, `strategy-kit` |
| `journal` | A structured entry for every decision, including when it did nothing | `trade` |
| `backtester` | Replays history through `research`, `trade`, and `journal`, with real fees and account limits | `journal` |
| `pine-bridge` | Pine versions of strategies, and the check for signal differences | `strategy-kit`, `backtester` |
| `api` | Local connection between the Python modules and the web app | `backtester`, `journal` |
| `web` | Vue.js app: strategy tests, charts, recommendations, and the journal | `api` |

**Build order:** `strategy-kit` → `research` → `trade` → `journal` → `backtester` → `pine-bridge`, `api` → `web`

## Decisions

- Each strategy supplies its own scan, evaluation, and exit rules. `research` and `trade` are the shared engines that run them.
- Strategies only see data up to a given time. That lets live runs and the backtester share code, and stops tests from using future prices.
- Alpaca is left out of Phase 1.
