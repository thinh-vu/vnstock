# Vnstock Data Schema Snapshot

**Version**: `4.0.3`
**Generated At**: `2026-05-02 09:07:11`

This document provides a comprehensive reference for the data structures and sample data returned by the Unified UI functions.

# 1. Core UI Functions

## `Market().equity('SSI').ohlcv()`
- **Module Context**: `Equity Market (KBS)`

### Schema
| Column | Type |
|--------|------|
| time | datetime64[ns] |
| open | float64 |
| high | float64 |
| low | float64 |
| close | float64 |
| volume | int64 |

### Sample Data
```json
[
  {
    "time": "2026-01-02T00:00:00",
    "open": 10.5,
    "high": 10.5,
    "low": 10.5,
    "close": 10.5,
    "volume": 1000
  },
  {
    "time": "2026-01-03T00:00:00",
    "open": 20.5,
    "high": 20.5,
    "low": 20.5,
    "close": 20.5,
    "volume": 2000
  },
  {
    "time": "2026-01-04T00:00:00",
    "open": 30.5,
    "high": 30.5,
    "low": 30.5,
    "close": 30.5,
    "volume": 3000
  }
]
```

---

## `Market().quote('SSI')`
- **Module Context**: `Market Global Quote (KBS)`

### Schema
| Column | Type |
|--------|------|
| symbol | object |
| exchange | object |
| ceiling_price | int64 |
| floor_price | int64 |
| reference_price | int64 |
| open_price | int64 |
| high_price | int64 |
| low_price | int64 |
| close_price | int64 |
| average_price | int64 |
| volume_accumulated | int64 |
| total_value | int64 |
| price_change | int64 |
| percent_change | int64 |
| bid_price_1 | object |
| bid_vol_1 | int64 |
| bid_price_2 | int64 |
| bid_vol_2 | int64 |
| bid_price_3 | int64 |
| bid_vol_3 | int64 |
| ask_price_1 | object |
| ask_vol_1 | int64 |
| ask_price_2 | int64 |
| ask_vol_2 | int64 |
| ask_price_3 | int64 |
| ask_vol_3 | int64 |
| foreign_buy_volume | int64 |
| foreign_sell_volume | int64 |
| foreign_room | int64 |

### Sample Data
```json
[
  {
    "symbol": "AAA",
    "exchange": "AAA",
    "ceiling_price": 1000,
    "floor_price": 1000,
    "reference_price": 1000,
    "open_price": 1000,
    "high_price": 1000,
    "low_price": 1000,
    "close_price": 1000,
    "average_price": 1000,
    "volume_accumulated": 1000,
    "total_value": 1000,
    "price_change": 1000,
    "percent_change": 1000,
    "bid_price_1": "string",
    "bid_vol_1": 1000,
    "bid_price_2": 1000,
    "bid_vol_2": 1000,
    "bid_price_3": 1000,
    "bid_vol_3": 1000,
    "ask_price_1": "string",
    "ask_vol_1": 1000,
    "ask_price_2": 1000,
    "ask_vol_2": 1000,
    "ask_price_3": 1000,
    "ask_vol_3": 1000,
    "foreign_buy_volume": 1000,
    "foreign_sell_volume": 1000,
    "foreign_room": 1000
  }
]
```

---

## `Reference().company('SSI').events()`
- **Module Context**: `Company Reference (KBS)`
- **Sample Ticker Used**: `SSI`

### Schema
| Column | Type |
|--------|------|
| id | object |
| event_name_vi | object |
| event_name_en | object |
| ticker | object |
| event_code | object |
| event_title_vi | object |
| event_title_en | object |
| display_date1 | object |
| public_date | object |
| exercise_ratio | float64 |
| category | object |
| display_date2 | object |
| issue_date | object |
| record_date | object |
| exright_date | object |
| start_date | object |
| end_date | object |
| action_type_vi | object |
| action_type_en | object |
| listing_date | object |
| payout_date | object |
| value_per_share | float64 |

### Sample Data
```json
[
  {
    "id": "string",
    "event_name_vi": "string",
    "event_name_en": "string",
    "ticker": "AAA",
    "event_code": "AAA",
    "event_title_vi": "string",
    "event_title_en": "string",
    "display_date1": "2026-01-02T00:00:00",
    "public_date": "2026-01-02",
    "exercise_ratio": 10.5,
    "category": "string",
    "display_date2": null,
    "issue_date": null,
    "record_date": null,
    "exright_date": null,
    "start_date": null,
    "end_date": null,
    "action_type_vi": null,
    "action_type_en": null,
    "listing_date": null,
    "payout_date": null,
    "value_per_share": null
  },
  {
    "id": "string",
    "event_name_vi": "string",
    "event_name_en": "string",
    "ticker": "AAA",
    "event_code": "AAA",
    "event_title_vi": "string",
    "event_title_en": "string",
    "display_date1": "2026-01-03T00:00:00",
    "public_date": "2026-01-03",
    "exercise_ratio": 20.5,
    "category": "string",
    "display_date2": null,
    "issue_date": null,
    "record_date": null,
    "exright_date": null,
    "start_date": null,
    "end_date": null,
    "action_type_vi": null,
    "action_type_en": null,
    "listing_date": null,
    "payout_date": null,
    "value_per_share": null
  },
  {
    "id": "string",
    "event_name_vi": "string",
    "event_name_en": "string",
    "ticker": "AAA",
    "event_code": "AAA",
    "event_title_vi": "string",
    "event_title_en": "string",
    "display_date1": "2026-01-04T00:00:00",
    "public_date": "2026-01-04",
    "exercise_ratio": null,
    "category": "string",
    "display_date2": "2026-01-04T00:00:00",
    "issue_date": "2026-01-04",
    "record_date": "2026-01-04",
    "exright_date": "2026-01-04",
    "start_date": null,
    "end_date": null,
    "action_type_vi": null,
    "action_type_en": null,
    "listing_date": null,
    "payout_date": null,
    "value_per_share": null
  }
]
```

---

## `Reference().company('SSI').info()`
- **Module Context**: `Company Reference (KBS)`
- **Sample Ticker Used**: `SSI`

### Schema
| Column | Type |
|--------|------|
| symbol | object |
| name | object |
| sector | object |
| profile | object |
| listing_date | object |
| issued_share | float64 |

### Sample Data
```json
[
  {
    "symbol": "AAA",
    "name": "string",
    "sector": "string",
    "profile": "string",
    "listing_date": "2026-01-02T00:00:00",
    "issued_share": 10.5
  }
]
```

---

## `Reference().company('SSI').news()`
- **Module Context**: `Company Reference (KBS)`
- **Sample Ticker Used**: `SSI`

### Schema
| Column | Type |
|--------|------|
| id | object |
| news_id | int64 |
| language | int64 |
| news_category_code | object |
| icb_code | object |
| com_group_code | object |
| ticker | object |
| news_title | object |
| friendly_title | object |
| news_sub_title | object |
| friendly_sub_title | object |
| news_short_content | object |
| news_full_content | object |
| news_image_url | object |
| news_small_image_url | object |
| news_source | object |
| news_source_link | object |
| news_author | object |
| news_keyword | object |
| friendly_keyword | object |
| public_date | object |

### Sample Data
```json
[
  {
    "id": "string",
    "news_id": 1000,
    "language": 1000,
    "news_category_code": null,
    "icb_code": null,
    "com_group_code": null,
    "ticker": null,
    "news_title": "string",
    "friendly_title": null,
    "news_sub_title": null,
    "friendly_sub_title": null,
    "news_short_content": null,
    "news_full_content": null,
    "news_image_url": "string",
    "news_small_image_url": "string",
    "news_source": null,
    "news_source_link": null,
    "news_author": null,
    "news_keyword": null,
    "friendly_keyword": null,
    "public_date": "2026-01-02T00:00:00"
  },
  {
    "id": "string",
    "news_id": 2000,
    "language": 2000,
    "news_category_code": null,
    "icb_code": null,
    "com_group_code": null,
    "ticker": null,
    "news_title": "string",
    "friendly_title": null,
    "news_sub_title": null,
    "friendly_sub_title": null,
    "news_short_content": null,
    "news_full_content": null,
    "news_image_url": "string",
    "news_small_image_url": "string",
    "news_source": null,
    "news_source_link": null,
    "news_author": null,
    "news_keyword": null,
    "friendly_keyword": null,
    "public_date": "2026-01-03T00:00:00"
  },
  {
    "id": "string",
    "news_id": 3000,
    "language": 3000,
    "news_category_code": null,
    "icb_code": null,
    "com_group_code": null,
    "ticker": null,
    "news_title": "string",
    "friendly_title": null,
    "news_sub_title": null,
    "friendly_sub_title": null,
    "news_short_content": null,
    "news_full_content": null,
    "news_image_url": "string",
    "news_small_image_url": "string",
    "news_source": null,
    "news_source_link": null,
    "news_author": null,
    "news_keyword": null,
    "friendly_keyword": null,
    "public_date": "2026-01-04T00:00:00"
  }
]
```

---

## `Reference().company('SSI').officers()`
- **Module Context**: `Company Reference (KBS)`
- **Sample Ticker Used**: `SSI`

### Schema
| Column | Type |
|--------|------|
| symbol | object |
| name | object |
| position | object |
| total_shares | int64 |
| rate | float64 |

### Sample Data
```json
[
  {
    "symbol": "AAA",
    "name": "string",
    "position": "string",
    "total_shares": 1000,
    "rate": 10.5
  },
  {
    "symbol": "AAA",
    "name": "string",
    "position": "string",
    "total_shares": 2000,
    "rate": 20.5
  },
  {
    "symbol": "AAA",
    "name": "string",
    "position": "string",
    "total_shares": 3000,
    "rate": 30.5
  }
]
```

---

## `Reference().company('SSI').shareholders()`
- **Module Context**: `Company Reference (KBS)`
- **Sample Ticker Used**: `SSI`

### Schema
| Column | Type |
|--------|------|
| symbol | object |
| name | object |
| total_shares | int64 |
| rate | float64 |
| date | object |

### Sample Data
```json
[
  {
    "symbol": "AAA",
    "name": "string",
    "total_shares": 1000,
    "rate": 10.5,
    "date": "2026-01-02T00:00:00"
  },
  {
    "symbol": "AAA",
    "name": "string",
    "total_shares": 2000,
    "rate": 20.5,
    "date": "2026-01-03T00:00:00"
  },
  {
    "symbol": "AAA",
    "name": "string",
    "total_shares": 3000,
    "rate": 30.5,
    "date": "2026-01-04T00:00:00"
  }
]
```

---

## `Reference().company('SSI').subsidiaries()`
- **Module Context**: `Company Reference (KBS)`
- **Sample Ticker Used**: `SSI`

### Schema
| Column | Type |
|--------|------|
| symbol | object |
| name | object |
| rate | float64 |
| sub_symbol | object |

### Sample Data
```json
[
  {
    "symbol": "AAA",
    "name": "string",
    "rate": 10.5,
    "sub_symbol": "AAA"
  },
  {
    "symbol": "AAA",
    "name": "string",
    "rate": 20.5,
    "sub_symbol": "AAA"
  },
  {
    "symbol": "AAA",
    "name": "string",
    "rate": 30.5,
    "sub_symbol": "AAA"
  }
]
```

---

## `Reference().equity.list()`
- **Module Context**: `Equity Reference (KBS)`

### Schema
| Column | Type |
|--------|------|
| symbol | object |
| organ_name | object |

### Sample Data
```json
[
  {
    "symbol": "AAA",
    "organ_name": "string"
  },
  {
    "symbol": "AAA",
    "organ_name": "string"
  },
  {
    "symbol": "AAA",
    "organ_name": "string"
  }
]
```

---

# 2. Financial Statements by Industry

## Industry: Banking
Universe Tickers: VCB, ACB, TCB, CTG

### Banking - Income Statement
- **Example Notation**: `Fundamental().equity('VCB').income_statement()`
- **Sample Ticker Used**: `VCB`
- **Module Context**: `Fundamental (Banking)`

#### Schema
| Column | Type |
|--------|------|
| item | object |
| item_id | object |
| 2025 | float64 |
| 2024 | float64 |
| 2023 | float64 |
| 2022 | float64 |

#### Sample Data
```json
[
  {
    "item": "string",
    "item_id": "string",
    "2025": 10.5,
    "2024": 10.5,
    "2023": 10.5,
    "2022": 10.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 20.5,
    "2024": 20.5,
    "2023": 20.5,
    "2022": 20.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 30.5,
    "2024": 30.5,
    "2023": 30.5,
    "2022": 30.5
  }
]
```

### Banking - Balance Sheet
- **Example Notation**: `Fundamental().equity('VCB').balance_sheet()`
- **Sample Ticker Used**: `VCB`
- **Module Context**: `Fundamental (Banking)`

#### Schema
| Column | Type |
|--------|------|
| item | object |
| item_id | object |
| 2025 | float64 |
| 2024 | float64 |
| 2023 | float64 |
| 2022 | float64 |

#### Sample Data
```json
[
  {
    "item": "string",
    "item_id": "string",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 20.5,
    "2024": 20.5,
    "2023": 20.5,
    "2022": 20.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 30.5,
    "2024": 30.5,
    "2023": 30.5,
    "2022": 30.5
  }
]
```

### Banking - Cash Flow
- **Example Notation**: `Fundamental().equity('VCB').cash_flow()`
- **Sample Ticker Used**: `VCB`
- **Module Context**: `Fundamental (Banking)`

#### Schema
| Column | Type |
|--------|------|
| item | object |
| item_id | object |
| 2025 | float64 |
| 2024 | float64 |
| 2023 | float64 |
| 2022 | float64 |

#### Sample Data
```json
[
  {
    "item": "string",
    "item_id": "string",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 20.5,
    "2024": 20.5,
    "2023": 20.5,
    "2022": 20.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 30.5,
    "2024": 30.5,
    "2023": 30.5,
    "2022": 30.5
  }
]
```

### Banking - Ratio
- **Example Notation**: `Fundamental().equity('VCB').ratio()`
- **Sample Ticker Used**: `VCB`
- **Module Context**: `Fundamental (Banking)`

#### Schema
| Column | Type |
|--------|------|
| item | object |
| item_id | object |
| 2026-Q1 | float64 |
| 2025-Q4 | float64 |
| 2025-Q4_1 | float64 |
| 2025-Q3 | float64 |

#### Sample Data
```json
[
  {
    "item": "string",
    "item_id": "string",
    "2026-Q1": 10.5,
    "2025-Q4": 10.5,
    "2025-Q4_1": 10.5,
    "2025-Q3": 10.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2026-Q1": 20.5,
    "2025-Q4": 20.5,
    "2025-Q4_1": 20.5,
    "2025-Q3": 20.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2026-Q1": 30.5,
    "2025-Q4": 30.5,
    "2025-Q4_1": 30.5,
    "2025-Q3": 30.5
  }
]
```

---

## Industry: Securities
Universe Tickers: SSI, VCI, HCM

### Securities - Income Statement
- **Example Notation**: `Fundamental().equity('SSI').income_statement()`
- **Sample Ticker Used**: `SSI`
- **Module Context**: `Fundamental (Securities)`

#### Schema
| Column | Type |
|--------|------|
| item | object |
| item_id | object |
| 2025 | float64 |
| 2024 | float64 |
| 2023 | float64 |
| 2022 | float64 |

#### Sample Data
```json
[
  {
    "item": "string",
    "item_id": "string",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 20.5,
    "2024": 20.5,
    "2023": 20.5,
    "2022": 20.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 30.5,
    "2024": 30.5,
    "2023": 30.5,
    "2022": 30.5
  }
]
```

### Securities - Balance Sheet
- **Example Notation**: `Fundamental().equity('SSI').balance_sheet()`
- **Sample Ticker Used**: `SSI`
- **Module Context**: `Fundamental (Securities)`

#### Schema
| Column | Type |
|--------|------|
| item | object |
| item_id | object |
| 2025 | float64 |
| 2024 | float64 |
| 2023 | float64 |
| 2022 | float64 |

#### Sample Data
```json
[
  {
    "item": "string",
    "item_id": "string",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 20.5,
    "2024": 20.5,
    "2023": 20.5,
    "2022": 20.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 30.5,
    "2024": 30.5,
    "2023": 30.5,
    "2022": 30.5
  }
]
```

### Securities - Cash Flow
- **Example Notation**: `Fundamental().equity('SSI').cash_flow()`
- **Sample Ticker Used**: `SSI`
- **Module Context**: `Fundamental (Securities)`

#### Schema
| Column | Type |
|--------|------|
| item | object |
| item_id | object |
| 2025 | float64 |
| 2024 | float64 |
| 2023 | float64 |
| 2022 | float64 |

#### Sample Data
```json
[
  {
    "item": "string",
    "item_id": "string",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 20.5,
    "2024": 20.5,
    "2023": 20.5,
    "2022": 20.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 30.5,
    "2024": 30.5,
    "2023": 30.5,
    "2022": 30.5
  }
]
```

### Securities - Ratio
- **Example Notation**: `Fundamental().equity('SSI').ratio()`
- **Sample Ticker Used**: `SSI`
- **Module Context**: `Fundamental (Securities)`

#### Schema
| Column | Type |
|--------|------|
| item | object |
| item_id | object |
| 2026-Q1 | float64 |
| 2025-Q4 | float64 |
| 2025-Q4_1 | float64 |
| 2025-Q3 | float64 |

#### Sample Data
```json
[
  {
    "item": "string",
    "item_id": "string",
    "2026-Q1": 10.5,
    "2025-Q4": 10.5,
    "2025-Q4_1": 10.5,
    "2025-Q3": 10.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2026-Q1": 20.5,
    "2025-Q4": 20.5,
    "2025-Q4_1": 20.5,
    "2025-Q3": 20.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2026-Q1": 30.5,
    "2025-Q4": 30.5,
    "2025-Q4_1": 30.5,
    "2025-Q3": 30.5
  }
]
```

---

## Industry: Insurance
Universe Tickers: BVH, PVI, PTI

### Insurance - Income Statement
- **Example Notation**: `Fundamental().equity('BVH').income_statement()`
- **Sample Ticker Used**: `BVH`
- **Module Context**: `Fundamental (Insurance)`

#### Schema
| Column | Type |
|--------|------|
| item | object |
| item_id | object |
| 2025 | float64 |
| 2024 | float64 |
| 2023 | float64 |
| 2022 | float64 |

#### Sample Data
```json
[
  {
    "item": "string",
    "item_id": "string",
    "2025": 10.5,
    "2024": 10.5,
    "2023": 10.5,
    "2022": 10.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 20.5,
    "2024": 20.5,
    "2023": 20.5,
    "2022": 20.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 30.5,
    "2024": 30.5,
    "2023": 30.5,
    "2022": 30.5
  }
]
```

### Insurance - Balance Sheet
- **Example Notation**: `Fundamental().equity('BVH').balance_sheet()`
- **Sample Ticker Used**: `BVH`
- **Module Context**: `Fundamental (Insurance)`

#### Schema
| Column | Type |
|--------|------|
| item | object |
| item_id | object |
| 2025 | float64 |
| 2024 | float64 |
| 2023 | float64 |
| 2022 | float64 |

#### Sample Data
```json
[
  {
    "item": "string",
    "item_id": "string",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 20.5,
    "2024": 20.5,
    "2023": 20.5,
    "2022": 20.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 30.5,
    "2024": 30.5,
    "2023": 30.5,
    "2022": 30.5
  }
]
```

### Insurance - Cash Flow
- **Example Notation**: `Fundamental().equity('BVH').cash_flow()`
- **Sample Ticker Used**: `BVH`
- **Module Context**: `Fundamental (Insurance)`

#### Schema
| Column | Type |
|--------|------|
| item | object |
| item_id | object |
| 2025 | float64 |
| 2024 | float64 |
| 2023 | float64 |
| 2022 | float64 |

#### Sample Data
```json
[
  {
    "item": "string",
    "item_id": "string",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 20.5,
    "2024": 20.5,
    "2023": 20.5,
    "2022": 20.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  }
]
```

### Insurance - Ratio
- **Example Notation**: `Fundamental().equity('BVH').ratio()`
- **Sample Ticker Used**: `BVH`
- **Module Context**: `Fundamental (Insurance)`

#### Schema
| Column | Type |
|--------|------|
| item | object |
| item_id | object |
| 2025-Q4 | float64 |
| 2025-Q3 | float64 |
| 2025-Q2 | float64 |
| 2025-Q1 | float64 |

#### Sample Data
```json
[
  {
    "item": "string",
    "item_id": "string",
    "2025-Q4": 10.5,
    "2025-Q3": 10.5,
    "2025-Q2": 10.5,
    "2025-Q1": 10.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2025-Q4": 20.5,
    "2025-Q3": 20.5,
    "2025-Q2": 20.5,
    "2025-Q1": 20.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2025-Q4": 30.5,
    "2025-Q3": 30.5,
    "2025-Q2": 30.5,
    "2025-Q1": 30.5
  }
]
```

---

## Industry: Regular
Universe Tickers: FPT, VIC, HPG, NVL

### Regular - Income Statement
- **Example Notation**: `Fundamental().equity('FPT').income_statement()`
- **Sample Ticker Used**: `FPT`
- **Module Context**: `Fundamental (Regular)`

#### Schema
| Column | Type |
|--------|------|
| item | object |
| item_id | object |
| 2025 | float64 |
| 2024 | float64 |
| 2023 | float64 |
| 2022 | float64 |

#### Sample Data
```json
[
  {
    "item": "string",
    "item_id": "string",
    "2025": 10.5,
    "2024": 10.5,
    "2023": 10.5,
    "2022": 10.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 20.5,
    "2024": 20.5,
    "2023": 20.5,
    "2022": 20.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 30.5,
    "2024": 30.5,
    "2023": 30.5,
    "2022": 30.5
  }
]
```

### Regular - Balance Sheet
- **Example Notation**: `Fundamental().equity('FPT').balance_sheet()`
- **Sample Ticker Used**: `FPT`
- **Module Context**: `Fundamental (Regular)`

#### Schema
| Column | Type |
|--------|------|
| item | object |
| item_id | object |
| 2025 | float64 |
| 2024 | float64 |
| 2023 | float64 |
| 2022 | float64 |

#### Sample Data
```json
[
  {
    "item": "string",
    "item_id": "string",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 20.5,
    "2024": 20.5,
    "2023": 20.5,
    "2022": 20.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 30.5,
    "2024": 30.5,
    "2023": 30.5,
    "2022": 30.5
  }
]
```

### Regular - Cash Flow
- **Example Notation**: `Fundamental().equity('FPT').cash_flow()`
- **Sample Ticker Used**: `FPT`
- **Module Context**: `Fundamental (Regular)`

#### Schema
| Column | Type |
|--------|------|
| item | object |
| item_id | object |
| 2025 | float64 |
| 2024 | float64 |
| 2023 | float64 |
| 2022 | float64 |

#### Sample Data
```json
[
  {
    "item": "string",
    "item_id": "string",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": 20.5,
    "2024": 20.5,
    "2023": 20.5,
    "2022": 20.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  }
]
```

### Regular - Ratio
- **Example Notation**: `Fundamental().equity('FPT').ratio()`
- **Sample Ticker Used**: `FPT`
- **Module Context**: `Fundamental (Regular)`

#### Schema
| Column | Type |
|--------|------|
| item | object |
| item_id | object |
| 2026-Q1 | float64 |
| 2025-Q4 | float64 |
| 2025-Q4_1 | float64 |
| 2025-Q3 | float64 |

#### Sample Data
```json
[
  {
    "item": "string",
    "item_id": "string",
    "2026-Q1": 10.5,
    "2025-Q4": 10.5,
    "2025-Q4_1": 10.5,
    "2025-Q3": 10.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2026-Q1": 20.5,
    "2025-Q4": 20.5,
    "2025-Q4_1": 20.5,
    "2025-Q3": 20.5
  },
  {
    "item": "string",
    "item_id": "string",
    "2026-Q1": 30.5,
    "2025-Q4": 30.5,
    "2025-Q4_1": 30.5,
    "2025-Q3": 30.5
  }
]
```

---
