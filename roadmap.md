# vnstock Roadmap — Trading Data Focus

> Goal: make `vnstock` a first-class data extraction library for algo-trading and quantitative finance on Vietnamese and global markets.  
> Architecture constraint: data extraction only, flat/open access, no user registration, no broker execution.

---

## Current State

### What Works

| Capability | Providers | Notes |
|---|---|---|
| OHLCV history (1m–1M) | KBS, VCI, MSN, FMP | KBS has native intervals; VCI resamples sub-hour from 1m |
| Multi-symbol price board | KBS, VCI | KBS: 3-level BBO; VCI: N-level BBO |
| Intraday tick tape (today only) | KBS, VCI | KBS: page/offset; VCI: cursor-based with native trade ID |
| Match type classification (buy/sell/ATO/ATC) | KBS, VCI | Derived from side + session time windows |
| Foreign flow (session total) | KBS (price_board) | Session totals only, not a time-series |
| Put-through trades (session total) | KBS (price_board) | Negotiated block trade qty/value |
| Open interest snapshot | KBS (derivatives) | Today only; no history |
| Forex/crypto OHLCV | MSN, FMP | MSN: daily + resample; FMP: global intraday |
| 30+ Vietnam indices OHLCV | VCI | Sector indices: VNIT, VNREAL, HNXFIN, etc. |
| Fundamental / company data | KBS, VCI, FMarket | Balance sheet, income, cash flow, ratios |

### Known Gaps

| Gap | Impact |
|---|---|
| No WebSocket / streaming | Cannot build live trading loops without polling boilerplate |
| `intraday()` is today-only | No historical tick replay or microstructure backtesting |
| `price_depth()` is a stub | Level 2 order book unreachable (URL + column map defined but no implementation) |
| Volume-by-price is a stub | KBS `/stock/matched-by-price` URL + map defined but no method calls it |
| `history()` is single-symbol | Universe scans require client-side loops |
| Foreign flow is session-only | No daily time-series for trend/signal construction |
| `foreign_trade()` / `prop_trade()` are stubs | No provider implementations wired |
| No OI time-series | Only snapshot; cannot track futures OI trend |
| No multi-day intraday chunker | Getting 5-day 1m OHLCV requires manual date-range splitting |

---

## Roadmap

### Phase 1 — Close obvious gaps (low effort, high signal)

**Goal**: Wire endpoints that are already defined in constants but have no callable method.

#### 1.1 Volume-by-price (match-by-price)

- KBS has `_STOCK_MATCHED_BY_PRICE_URL` and `_MATCHED_BY_PRICE_MAP` (columns: `price`, `buy_volume`, `sell_volume`, `unknown_volume`, `total_volume`)
- Implement `Quote.price_depth(symbol)` in `vnstock/explorer/kbs/quote.py`
- Expose through `Market.equity.quote` UI path

Unlocks: session VWAP, intraday liquidity zones, market profile analysis.

#### 1.2 Multi-symbol OHLCV batch

- Add `Quote.history_batch(symbols: list[str], start, end, interval, ...)` to the UI layer
- Fan out single-symbol `history()` calls with `ThreadPoolExecutor` or `asyncio`
- Return `dict[str, DataFrame]` or a MultiIndex DataFrame

Unlocks: universe scanning, correlation matrices, cointegration tests, portfolio analytics.

#### 1.3 Historical foreign flow series

- KBS has `_RANKING_FOREIGN_URL = /rtranking/foreignTotal` already defined
- Implement `Trading.foreign_flow(symbol, start, end)` returning daily `buy_volume`, `sell_volume`, `net_volume` series
- Expose through `Market.equity.trading`

Unlocks: foreign buying trend signals, 3/5/10-day cumulative foreign flow, sector rotation tracking.

#### 1.4 Level 2 order book from VCI price board

- VCI `price_board()` already returns N-level `bidAsk_bid_N_price/volume` and `bidAsk_ask_N_price/volume`
- Add `Market.equity.trading.price_depth(symbols)` that extracts and structures bid/ask depth from the existing `price_board()` response into a clean `[(price, volume, side)]` format
- No new endpoint needed for VCI

Unlocks: spread analysis, order book imbalance signals, liquidity estimation.

---

### Phase 2 — Structural improvements (medium effort, high trading value)

#### 2.1 Streaming / polling adapter

Add a `Watcher` class that wraps `price_board()` and `intraday()` in a configurable poll loop emitting DataFrames via a generator or callback. No WebSocket required at this stage — makes the interface look like a stream.

```python
# Target API
watcher = Market.equity.watcher(["VCB", "TCB"], interval=3)
for tick in watcher.stream():
    process(tick)
```

Unlocks: live strategy loops, real-time signal computation, paper trading engines.

#### 2.2 Multi-day intraday OHLCV chunker

- `history()` with 1m/5m intervals needs multiple requests for multi-day ranges
- Add intelligent request chunker inside `Quote.history()` that auto-splits long date ranges into provider-safe windows and stitches results transparently
- Expose `max_bars_per_request` as a provider-level constant

Unlocks: multi-day intraday backtests without client-side loop boilerplate.

#### 2.3 Rate-limit / throttle manager

- `history_batch` and `Watcher` will immediately hit provider rate limits
- Add a provider-scoped token-bucket or sliding-window throttle manager in `vnstock/core/`
- Configurable via `VNSTOCK_RATE_LIMIT_*` env vars

Unlocks: safe bulk downloads and continuous polling without 429 failures.

#### 2.4 Tick history investigation and implementation

- Verify whether KBS/VCI intraday endpoints accept historical date parameters (not just today)
- If supported: implement `Quote.intraday_history(symbol, dates: list[str])` that fetches and concatenates tick data across dates
- If not: document the limitation clearly

Unlocks: tick replay, microstructure analysis, execution quality analytics.

---

### Phase 3 — Advanced trading data (new endpoints, higher effort)

#### 3.1 Open interest history (derivatives)

- Investigate if KBS/VCI expose historical OI endpoints for VN30F, VNXFC
- Implement `Derivatives.oi_history(symbol, start, end)` if available
- Expose through `Market.derivatives` UI path

Unlocks: OI/price divergence signals, futures roll tracking, term structure analysis.

#### 3.2 Sector/index membership history

- Add `Reference.index_members(index, date)` supporting historical constituent lookup
- Data source: VCI has 30+ sector indices already; membership change events are likely available

Unlocks: proper index-constituent backtesting, index inclusion/exclusion event studies.

#### 3.3 VCI derivatives coverage expansion

- Audit VCI's derivatives API coverage vs KBS
- VCI may have better OI, intraday depth, or historical data for futures
- Add VCI as a secondary provider for `Derivatives` domain

#### 3.4 Prop/dealer flow data

- Investigate whether any provider exposes proprietary/dealer trading flow
- `Trading.prop_trade()` and `Trading.side_stats()` are already stubbed in `api/trading.py`
- Wire to a real backend if data is available

---

## Priority Matrix

```
  High Impact
     │
     │   1.1 vol-by-price ──── immediate: URL+map already defined
     │   1.2 history_batch ─── immediate: fan-out of existing method
     │   1.3 foreign_flow ──── immediate: URL already defined
     │   1.4 L2 order book ─── immediate: data already in price_board
     │
     │   2.1 Watcher/stream ── medium: new architecture, high trading value
     │   2.2 intraday chunker ─ medium: transparent improvement to history()
     │   2.3 throttle manager ─ medium: needed before batch/stream usage
     │
     │   3.x advanced data ─── harder: needs endpoint investigation first
     │
     └────────────────────────────────────────────────────────────
          Low Effort ─────────────────────────────── High Effort
```

**Start here**: Phase 1 items — all are wiring existing constants/URLs to callable methods. Highest capability-to-effort ratio.

**Biggest unlock**: Phase 2.1 `Watcher` — enables live trading loop integration without waiting for a true WebSocket feed.

---

## Provider Capability Matrix (current)

| Capability | KBS | VCI | MSN | FMP | DNSE |
|---|:---:|:---:|:---:|:---:|:---:|
| Intraday OHLCV 1m (native) | yes | yes | no | yes (global) | yes |
| Intraday OHLCV 5m/15m/30m (native) | yes | resample | no | yes (global) | yes |
| Intraday OHLCV 1h (native) | yes | yes | no | yes (global) | yes |
| Daily/Weekly/Monthly OHLCV | yes | yes | yes | yes | yes |
| Tick tape (today only) | yes | yes | no | no | yes |
| Historical tick data | no | no | no | no | no |
| Price board multi-symbol | yes (3-level) | yes (N-level) | no | no | yes |
| Foreign flow (session) | yes | partial | no | no | yes |
| Foreign flow (time-series) | stub | no | no | no | no |
| Volume-by-price | stub | no | no | no | no |
| Level 2 order book | no | in price_board | no | no | no |
| Open interest (today) | yes (futures) | no | no | no | no |
| Open interest (history) | unknown | unknown | no | no | no |
| Prop/dealer flow | no | no | no | no | no |
| Forex/crypto OHLCV | no | no | yes | yes | no |
| Vietnam sector indices | 6 indices | 30+ indices | no | no | no |
| WebSocket / streaming | no | no | no | no | no |

---

*Last updated: 2026-07-02*
