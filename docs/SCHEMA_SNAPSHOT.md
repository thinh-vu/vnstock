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
    "time": "2025-12-03T07:00:00",
    "open": 29.54,
    "high": 29.67,
    "low": 29.31,
    "close": 29.49,
    "volume": 22047800
  },
  {
    "time": "2025-12-04T07:00:00",
    "open": 29.67,
    "high": 30.22,
    "low": 29.63,
    "close": 29.9,
    "volume": 32017100
  },
  {
    "time": "2025-12-05T07:00:00",
    "open": 30.04,
    "high": 30.08,
    "low": 29.35,
    "close": 29.4,
    "volume": 47092900
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
    "symbol": "SSI",
    "exchange": "HOSE",
    "ceiling_price": 29550,
    "floor_price": 25750,
    "reference_price": 27650,
    "open_price": 27700,
    "high_price": 27900,
    "low_price": 27650,
    "close_price": 27650,
    "average_price": 27723,
    "volume_accumulated": 12241100,
    "total_value": 339364725000,
    "price_change": 0,
    "percent_change": 0,
    "bid_price_1": "27650.0",
    "bid_vol_1": 788400,
    "bid_price_2": 27600,
    "bid_vol_2": 342700,
    "bid_price_3": 27550,
    "bid_vol_3": 236600,
    "ask_price_1": "27700.0",
    "ask_vol_1": 4500,
    "ask_price_2": 27750,
    "ask_vol_2": 173400,
    "ask_price_3": 27800,
    "ask_vol_3": 139800,
    "foreign_buy_volume": 1016300,
    "foreign_sell_volume": 1149827,
    "foreign_room": 1693626494
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
    "id": "69f14f8edb487120c68b4cf7",
    "event_name_vi": "Phát hành cổ phiếu",
    "event_name_en": "Share Issue",
    "ticker": "SSI",
    "event_code": "ISS",
    "event_title_vi": "Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.3%",
    "event_title_en": "Share Issue - ESOP ratio 0.3%",
    "display_date1": "2026-04-28T00:00:00",
    "public_date": "2026-04-28",
    "exercise_ratio": 0.0033,
    "category": "DIVIDEND",
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
    "id": "69f14f8edb487120c68b4cf6",
    "event_name_vi": "Phát hành cổ phiếu",
    "event_name_en": "Share Issue",
    "ticker": "SSI",
    "event_code": "ISS",
    "event_title_vi": "Phát hành cổ phiếu - Cổ phiếu thưởng tỉ lệ 20.0%",
    "event_title_en": "Share Issue - Bonus Issue ratio 20.0%",
    "display_date1": "2026-04-28T00:00:00",
    "public_date": "2026-04-28",
    "exercise_ratio": 0.2,
    "category": "DIVIDEND",
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
    "id": "698e6f07f24a113a2fd766ad",
    "event_name_vi": "Đại hội Đồng Cổ đông",
    "event_name_en": "Annual General Meeting",
    "ticker": "SSI",
    "event_code": "AGME",
    "event_title_vi": "SSI - Tổ chức ĐHĐCĐ thường niên 2026",
    "event_title_en": "SSI - Holds 2026 AGM",
    "display_date1": "2026-04-23T00:00:00",
    "public_date": "2026-02-13",
    "exercise_ratio": null,
    "category": "SHAREHOLDER_MEETING",
    "display_date2": "2026-03-16T00:00:00",
    "issue_date": "2026-04-23",
    "record_date": "2026-03-17",
    "exright_date": "2026-03-16",
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
    "symbol": "SSI",
    "name": "Công ty Cổ phần Chứng khoán SSI",
    "sector": "Financial Services",
    "profile": "Công ty Cổ phần Chứng khoán SSI (SSI) có tiền thân là Công ty Cổ phần Chứng khoán Sài Gòn được thành lập vào năm 1999. SSI chuyên cung cấp dịch vụ môi giới, tư vấn và đầu tư tài chính, chứng khoán với mạng lưới hoạt động rộng tại những thành phố lớn như Hà Nội, Thành phố Hồ Chí Minh, Hải Phòng, Nha Trang, Vũng Tàu. Công ty đã cung cấp dịch vụ cho các nhà đầu tư trong nước và nhiều nhà đầu tư nước ngoài danh tiếng với các khách hàng tiêu biểu như Công ty bao gồm Morgan Stanley, HSBC, Vinamilk, Credit Suisse, BIDV, ANZ, Prudential VN, Deutsche Bank. Trong năm 2025, Công ty xếp ở vị trí 2 với 11.53% thị phần môi giới cổ phiếu niêm yết tại HOSE, vị trí thứ 3 với 8.18% thị phần môi giới cổ phiếu niêm yết tại HNX và vị trí thứ 3 với 7.07% thị phần môi giới cổ phiếu đăng ký giao dịch trên thị trường UPCOM. Trên thị trường phái sinh, SSI đứng vị trí thứ 5 thị phần môi giới chứng khoán phái sinh với 5.09%. Doanh thu nghiệp vụ môi giới chứng khoán có giá trị bằng 2.344,72 tỷ đồng, tăng 40.62% so với cùng kỳ. Nợ vay ký quỹ/Vốn chủ sở hữu ở mức 120.43%, tăng 39.11%. Lợi nhuận trước thuế có giá trị bằng 5.082,97 tỷ đồng, tăng 43.44%. Tỷ lệ sinh lời trên vốn chủ sở hữu (ROE) ở mức 14.01%, tăng 3.15%. Cổ phiếu của Công ty được niêm yết trên sàn HNX vào năm 2006 và chuyển sang sàn HOSE từ năm 2007.",
    "listing_date": "2006-12-15T00:00:00",
    "issued_share": 2491097752.0
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
    "id": "69f14fc9db487120c68b4edf",
    "news_id": 11989043,
    "language": 0,
    "news_category_code": null,
    "icb_code": null,
    "com_group_code": null,
    "ticker": null,
    "news_title": "SSI: Thông báo thay đổi nhân sự - Miễn nhiệm và bổ nhiệm thành viên HĐQT",
    "friendly_title": null,
    "news_sub_title": null,
    "friendly_sub_title": null,
    "news_short_content": null,
    "news_full_content": null,
    "news_image_url": "https://cdn.fiingroup.vn/medialib/127889/I/2024/11/26/09481833153750700_SSI-1.png",
    "news_small_image_url": "",
    "news_source": null,
    "news_source_link": null,
    "news_author": null,
    "news_keyword": null,
    "friendly_keyword": null,
    "public_date": "2026-04-28T15:39:00"
  },
  {
    "id": "69f14fc9db487120c68b4db9",
    "news_id": 11988204,
    "language": 0,
    "news_category_code": null,
    "icb_code": null,
    "com_group_code": null,
    "ticker": null,
    "news_title": "SSI: Nghị quyết và Biên bản họp ĐHĐCĐ thường niên 2026",
    "friendly_title": null,
    "news_sub_title": null,
    "friendly_sub_title": null,
    "news_short_content": null,
    "news_full_content": null,
    "news_image_url": "https://cdn.fiingroup.vn/medialib/127889/I/2024/11/26/09481833153750700_SSI-1.png",
    "news_small_image_url": "",
    "news_source": null,
    "news_source_link": null,
    "news_author": null,
    "news_keyword": null,
    "friendly_keyword": null,
    "public_date": "2026-04-28T10:38:12"
  },
  {
    "id": "69ed5b6edb487120c685f76d",
    "news_id": 11986037,
    "language": 0,
    "news_category_code": null,
    "icb_code": null,
    "com_group_code": null,
    "ticker": null,
    "news_title": "ĐHCĐ SSI: Dư nợ margin có thể lên tới 45.000 tỷ đồng",
    "friendly_title": null,
    "news_sub_title": null,
    "friendly_sub_title": null,
    "news_short_content": null,
    "news_full_content": null,
    "news_image_url": "https://cdn.fiingroup.vn/medialib/127379/I/2026/04/24/img32911321913_11593764613310700.jpg",
    "news_small_image_url": "",
    "news_source": null,
    "news_source_link": null,
    "news_author": null,
    "news_keyword": null,
    "friendly_keyword": null,
    "public_date": "2026-04-24T11:47:00"
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
    "symbol": "SSI",
    "name": "Nguyễn Duy Hưng",
    "position": "Chủ tịch Hội đồng Quản trị",
    "total_shares": 19416198,
    "rate": 0.00779
  },
  {
    "symbol": "SSI",
    "name": "Nguyễn Hồng Nam",
    "position": "Thành viên Hội đồng Quản trị",
    "total_shares": 9961615,
    "rate": 0.004
  },
  {
    "symbol": "SSI",
    "name": "Nguyễn Duy Khánh",
    "position": "Thành viên Hội đồng Quản trị",
    "total_shares": 5698435,
    "rate": 0.00229
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
    "symbol": "SSI",
    "name": "Daiwa Securities Group Inc",
    "total_shares": 380585607,
    "rate": 0.15265,
    "date": "2026-01-26T09:10:35.883"
  },
  {
    "symbol": "SSI",
    "name": "Công ty TNHH Đầu Tư Ndh",
    "total_shares": 197116185,
    "rate": 0.07907,
    "date": "2026-01-26T09:10:46.203"
  },
  {
    "symbol": "SSI",
    "name": "Công ty TNHH Bất Động Sản Sài Gòn Đan Linh",
    "total_shares": 91885664,
    "rate": 0.03685,
    "date": "2026-01-09T17:52:07.347"
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
    "symbol": "SSI",
    "name": "Công ty TNHH Quản lý quỹ SSI",
    "rate": 1.0,
    "sub_symbol": "SSIAM"
  },
  {
    "symbol": "SSI",
    "name": "Quỹ Đầu Tư Thành Viên SSI",
    "rate": 0.7615,
    "sub_symbol": "SSIIMF"
  },
  {
    "symbol": "SSI",
    "name": "Quỹ Đầu Tư Công Nghệ Số Việt Nam",
    "rate": 0.2,
    "sub_symbol": "2040155"
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
    "symbol": "GVT",
    "organ_name": "CTCP Giấy Việt Trì"
  },
  {
    "symbol": "MGC",
    "organ_name": "CTCP Địa chất mỏ - TKV"
  },
  {
    "symbol": "VID",
    "organ_name": "CTCP Đầu tư Phát triển Thương mại Viễn Đông"
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
    "item": "1. Thu nhập lãi và các khoản thu nhập tương tự",
    "item_id": "n_1.interest_income_and_similar_income",
    "2025": 105216484000.0,
    "2024": 93654841000.0,
    "2023": 108122278000.0,
    "2022": 88112700000.0
  },
  {
    "item": "2. Chi phí lãi và các chi phí tương tự",
    "item_id": "n_2.interest_expense_and_similar_expenses",
    "2025": 46445074000.0,
    "2024": 38249106000.0,
    "2023": 54501409000.0,
    "2022": 34866222000.0
  },
  {
    "item": "I. Thu nhập lãi thuần",
    "item_id": "i.net_interest_income",
    "2025": 58771410000.0,
    "2024": 55405735000.0,
    "2023": 53620869000.0,
    "2022": 53246478000.0
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
    "item": "A. TÀI SẢN",
    "item_id": "assets",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "I. Tiền mặt, vàng bạc, đá quý",
    "item_id": "i.cash_gold_and_silver_precious_stones",
    "2025": 15542769000.0,
    "2024": 14268064000.0,
    "2023": 14504849000.0,
    "2022": 18348534000.0
  },
  {
    "item": "II. Tiền gửi tại NHNN",
    "item_id": "ii.balances_with_the_state_bank_of_vietnam",
    "2025": 37445504000.0,
    "2024": 49340493000.0,
    "2023": 58104503000.0,
    "2022": 92557809000.0
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
    "item": "Lưu chuyển tiền từ hoạt động kinh doanh",
    "item_id": "i.cash_flows_from_operating_activities",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "1. Thu nhập lãi và các khoản thu nhập tương tự nhận được",
    "item_id": "n_1.receipts_from_interest_and_similar_income",
    "2025": 104376654000.0,
    "2024": 93772270000.0,
    "2023": 108115649000.0,
    "2022": 86084771000.0
  },
  {
    "item": "2. Chi phí lãi và các chi phí tương tự đã trả ",
    "item_id": "n_2.payments_for_interest_and_similar_expenses",
    "2025": -44982264000.0,
    "2024": -43790244000.0,
    "2023": -47454819000.0,
    "2022": -31709129000.0
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
    "item": "Thu nhập trên mỗi cổ phần của 4 quý gần nhất (EPS)",
    "item_id": "trailing_eps",
    "2026-Q1": 4542.29,
    "2025-Q4": 5008.22,
    "2025-Q4_1": 6037.9,
    "2025-Q3": 5501.45
  },
  {
    "item": "Giá trị sổ sách của cổ phiếu (BVPS)",
    "item_id": "book_value_per_share_bvps",
    "2026-Q1": 27231.3,
    "2025-Q4": 26663.5,
    "2025-Q4_1": 24527.26,
    "2025-Q3": 25581.35
  },
  {
    "item": "Chỉ số giá thị trường trên thu nhập (P/E)",
    "item_id": "p_e",
    "2026-Q1": 12.66,
    "2025-Q4": 12.38,
    "2025-Q4_1": 10.6,
    "2025-Q3": 10.36
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
    "item": "I. DOANH THU HOẠT ĐỘNG",
    "item_id": "operating_income",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "1.1. Lãi từ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)",
    "item_id": "n_1.1.gains_from_financial_assets_at_fair_value_through_profit_or_loss_fvtpl",
    "2025": 6160760603.0,
    "2024": 4021594603.0,
    "2023": 3166865051.0,
    "2022": 2020267370.0
  },
  {
    "item": "a. Lãi bán các tài sản tài chính",
    "item_id": "a.realised_gains_on_disposals_of_fvtpl_financial_assets",
    "2025": 3137405005.0,
    "2024": 1418748423.0,
    "2023": 1087667751.0,
    "2022": 987264064.0
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
    "item": "TÀI SẢN ",
    "item_id": "assets",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "A. TÀI SẢN NGẮN HẠN",
    "item_id": "a.short_term_assets",
    "2025": 89322786682.0,
    "2024": 70932391912.0,
    "2023": 65755288990.0,
    "2022": 48731915105.0
  },
  {
    "item": "I. Tài sản tài chính ngắn hạn",
    "item_id": "short_term_financial_assets",
    "2025": 89191517712.0,
    "2024": 70813502225.0,
    "2023": 65659269541.0,
    "2022": 48621880320.0
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
    "item": "I. LƯU CHUYỂN TIỀN TỪ HOẠT ĐỘNG KINH DOANH CHỨNG KHOÁN",
    "item_id": "i.cash_flow_from_securities_trading_activities",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "1. Lợi nhuận trước thuế",
    "item_id": "n_1.profit_before_tax",
    "2025": 5082973996.0,
    "2024": 3543527484.0,
    "2023": 2848566970.0,
    "2022": 2109703392.0
  },
  {
    "item": "2. Điều chỉnh cho các khoản",
    "item_id": "n_2.adjustments_for",
    "2025": -3413468699.0,
    "2024": -2742429544.0,
    "2023": -2006045912.0,
    "2022": -1704479484.0
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
    "item": "Thu nhập trên mỗi cổ phần của 4 quý gần nhất (EPS)",
    "item_id": "trailing_eps",
    "2026-Q1": 2052.63,
    "2025-Q4": 1911.6,
    "2025-Q4_1": 1706.52,
    "2025-Q3": 1668.51
  },
  {
    "item": "Giá trị sổ sách của cổ phiếu (BVPS)",
    "item_id": "book_value_per_share_bvps",
    "2026-Q1": 15446.84,
    "2025-Q4": 15056.24,
    "2025-Q4_1": 14120.87,
    "2025-Q3": 14580.77
  },
  {
    "item": "Chỉ số giá thị trường trên thu nhập (P/E)",
    "item_id": "p_e",
    "2026-Q1": 14.74,
    "2025-Q4": 20.17,
    "2025-Q4_1": 15.24,
    "2025-Q3": 14.8
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
    "item": "1. Doanh thu phí bảo hiểm (01= (01.1+01.2-01.3)",
    "item_id": "n_1.insurance_premium_01_01_1_01_2_01_3",
    "2025": 43728345354.0,
    "2024": 42669681560.0,
    "2023": 42659877832.0,
    "2022": 42650508302.0
  },
  {
    "item": "- Thu phí bảo hiểm gốc",
    "item_id": "n_1.gross_written_premium",
    "2025": 43716183433.0,
    "2024": 42591775980.0,
    "2023": 42637147156.0,
    "2022": 42961317756.0
  },
  {
    "item": "- Thu phí nhận tái bảo hiểm",
    "item_id": "n_2.reinsurance_premium_assumed",
    "2025": 399971248.0,
    "2024": 217571102.0,
    "2023": 214862851.0,
    "2022": 159740171.0
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
    "item": "TÀI SẢN ",
    "item_id": "assets",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "A. TÀI SẢN NGẮN HẠN (100=110+120+130+140+150+190)",
    "item_id": "a.short_term_assets",
    "2025": 150363051574.0,
    "2024": 121226741292.0,
    "2023": 122398176223.0,
    "2022": 117373071557.0
  },
  {
    "item": "I.   Tiền và các khoản tương đương tiền",
    "item_id": "i.cash_and_cash_equivalents",
    "2025": 4194682648.0,
    "2024": 1464088127.0,
    "2023": 4783513587.0,
    "2022": 2206497560.0
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
    "item": "I. Lưu chuyển tiền từ hoạt động kinh doanh",
    "item_id": "i.cash_flows_from_operating_activities",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "1. Lợi nhuận trước thuế",
    "item_id": "n_1.profit_before_tax",
    "2025": 3554431272.0,
    "2024": 2663171477.0,
    "2023": 2236298700.0,
    "2022": 2010163564.0
  },
  {
    "item": "2. Điều chỉnh cho các khoản:",
    "item_id": "n_2_adjustments_for",
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
    "item": "Thu nhập trên mỗi cổ phần của 4 quý gần nhất (EPS)",
    "item_id": "trailing_eps",
    "2025-Q4": 4012.27,
    "2025-Q3": 3577.84,
    "2025-Q2": 3262.31,
    "2025-Q1": 2924.74
  },
  {
    "item": "Giá trị sổ sách của cổ phiếu (BVPS)",
    "item_id": "book_value_per_share_bvps",
    "2025-Q4": 34499.89,
    "2025-Q3": 34429.53,
    "2025-Q2": 33411.91,
    "2025-Q1": 32671.29
  },
  {
    "item": "Chỉ số giá thị trường trên thu nhập (P/E)",
    "item_id": "p_e",
    "2025-Q4": 14.16,
    "2025-Q3": 15.46,
    "2025-Q2": 16.28,
    "2025-Q1": 18.22
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
    "item": "1. Doanh thu bán hàng và cung cấp dịch vụ ",
    "item_id": "n_1.revenue",
    "2025": 70207688945.0,
    "2024": 62962652135.0,
    "2023": 52625174861.0,
    "2022": 44023010881.0
  },
  {
    "item": "2. Các khoản giảm trừ doanh thu",
    "item_id": "n_2.deduction_from_revenue",
    "2025": 94863844.0,
    "2024": 113857783.0,
    "2023": 7274034.0,
    "2022": 13483200.0
  },
  {
    "item": "3. Doanh thu thuần về bán hàng và cung cấp dịch vụ",
    "item_id": "n_3.net_revenue",
    "2025": 70112825101.0,
    "2024": 62848794351.0,
    "2023": 52617900827.0,
    "2022": 44009527681.0
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
    "item": "TÀI SẢN ",
    "item_id": "assets",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "A. TÀI SẢN NGẮN HẠN",
    "item_id": "a.short_term_assets",
    "2025": 58137438255.0,
    "2024": 45535942846.0,
    "2023": 36705751752.0,
    "2022": 30937711076.0
  },
  {
    "item": "I. Tiền và các khoản tương đương tiền",
    "item_id": "i.cash_and_cash_equivalents",
    "2025": 10522105730.0,
    "2024": 9315440439.0,
    "2023": 8279156683.0,
    "2022": 6440177174.0
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
    "item": "I. Lưu chuyển tiền từ hoạt động kinh doanh",
    "item_id": "i_cash_flows_from_operating_activities",
    "2025": null,
    "2024": null,
    "2023": null,
    "2022": null
  },
  {
    "item": "1. Lợi nhuận trước thuế",
    "item_id": "n_1.profit_before_tax",
    "2025": 13043632834.0,
    "2024": 11069666418.0,
    "2023": 9203006099.0,
    "2022": 7662282960.0
  },
  {
    "item": "2. Điều chỉnh cho các khoản",
    "item_id": "n_2_adjustments_for",
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
    "item": "Thu nhập trên mỗi cổ phần của 4 quý gần nhất (EPS)",
    "item_id": "trailing_eps",
    "2026-Q1": 6016.81,
    "2025-Q4": 5988.42,
    "2025-Q4_1": 5772.14,
    "2025-Q3": 5862.01
  },
  {
    "item": "Giá trị sổ sách của cổ phiếu (BVPS)",
    "item_id": "book_value_per_share_bvps",
    "2026-Q1": 25682.0,
    "2025-Q4": 25141.0,
    "2025-Q4_1": 25759.0,
    "2025-Q3": 26918.0
  },
  {
    "item": "Chỉ số giá thị trường trên thu nhập (P/E)",
    "item_id": "p_e",
    "2026-Q1": 15.92,
    "2025-Q4": 15.53,
    "2025-Q4_1": 20.96,
    "2025-Q3": 20.16
  }
]
```

---

