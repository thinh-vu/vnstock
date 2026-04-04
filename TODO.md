# 8X API Calls + 5X Speed Optimization TODO
## Current Progress: Phase 1 ⏳

## Phase 1 COMPLETE ✓
- [x] `async_client.py` created (httpx.AsyncClient + RateLimiter 500/min)
- [x] `__init__.py` exports (async_send_request, fetch_multiple_requests)
- [x] `proxy_manager.py` enhanced (get_proxy_pool(16))
- [x] requirements.txt + deps installed

**Ready for Phase 2: Quote parallelization** (user priority)

## Phase 2: Quote (vci/kbs → async + parallel)

## Phase 2: Quote Parallelization (Priority: quote/listing first)
- [ ] `vnstock/explorer/vci/quote.py`: Add async history(), fetch_multiple(symbols)
- [ ] `vnstock/explorer/kbs/quote.py`: Add async history(), fetch_multiple()
- [ ] `vnstock/api/quote.py`: Add quote_multiple(symbols, parallel=True)

## Phase 3: Listing + Financial
- [ ] `vnstock/explorer/vci/listing.py`: symbols_parallel(groups)
- [ ] `vnstock/explorer/kbs/listing.py`: Similar  
- [ ] `vnstock/api/listing.py`: listing_parallel()

## Phase 4: Productionize
- [ ] **DEPS**: httpx[http2], asyncio-throttle → requirements.txt
- [ ] Tests: pytest-asyncio + httpx-mock
- [ ] Benchmark script
- [ ] Docs + examples

## Phase 5: Advanced
- [ ] Caching (LRU)
- [ ] Metrics dashboard

**Metrics Target**: 500 req/min safe, 8X calls, 5X processing speed
**User Priority**: quote/listing first ✓

