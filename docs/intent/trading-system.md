# Trading System: Statement of Intent

Confirmed 2026-11-05.

## Outcome

A Python and TypeScript/Vue.js monorepo of connected trading projects, running locally on a Windows PC, built in three phases:

- **Phase 1:** the system recommends trades, and the owner places any trades manually.
- **Phase 2:** scanner, analyzer, and trader agents run at scale and ask for approval in the UI.
- **Phase 3:** the system trades fully automatically, on a server by then.

## Why

- Learn how to build a large project with Claude.
- Find out with real evidence whether the strategies can make a profit.

The owner is the only user.

## Phase 1 scope

- **Core pipeline:** research (market data, news, technical signals, and a scanner that builds the watchlist), trade (evaluate the research and decide buy, sell, or hold), and journal (a structured entry for every decision, including when it did nothing).
- **Supporting projects:** strategy definition, a backtester, and a Vue.js web app, all for US stocks. See `CAPABILITY-MAP.md` for the modules.
- **Web app:** select a strategy, set test parameters, run the backtest, and see results. It also shows recommended trades on TradingView-style charts with entry, stop, target, and the reason.
- **Adding strategies:** the owner describes a strategy to Claude Code, which follows written rules and a fixed project structure. The new strategy appears in the UI with no UI changes.
- **TradingView:** a generated Pine version of each strategy provides replay and live buy, sell, stop, and take-profit markers. The main code stays the source of truth, and an automatic check flags signal differences between the two versions. Some strategies may not translate fully.

## Success

On a trading day, the owner opens the app, sees a short ranked list from strategies that passed the backtester, and would actually trade from it.

## Constraints

- The backtester and live recommendations run the same code.
- A strategy must pass the backtest before it can make live recommendations.
- Backtests default to a $1,000 account, at most 2 positions, and fees of $0.01 per share with a $2.50 minimum per order, charged on both the buy and the sell. All are adjustable.
- Each strategy declares its own timeframe, since day versus swing trading is undecided.
- Use the large-project practices that pay off: short specs, task plans, tests, and review.
- Keep it easy to move to a server by Phase 3.

## Accounts

- **Paper:** Alpaca. It is not connected in Phase 1, where decisions are only recorded in the journal. Paper orders with approval start in Phase 2.
- **Real:** $1,000 to start, with the fees listed under Constraints. Alpaca paper results will not reflect these fees unless the system applies them itself.

## Decided later

- Scan and analysis rules
- Backtest pass criteria
- Long or short
- Day or swing trading
- Data source (assumed free first, paid only if a strategy needs it; not confirmed)

## Out of scope for Phase 1

- Placing orders or connecting a broker
- Options
- Non-US markets
- A visual strategy builder
- An agent chat inside the app
- Cloud hosting

## To verify during the spec

These came from memory and have not been checked:

- TradingView Pine Script and replay limits
- US day-trading rules for small margin and cash accounts
- Market data source options, especially intraday history and delisted stocks
- Historical news sources, since strategies that rely on news may not be fully testable in the backtester
