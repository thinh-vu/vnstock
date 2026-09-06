# Vnstock - Công Cụ Python Mã Nguồn Công Khai Cho Thị Trường Chứng Khoán Việt Nam

[![Vnstock Homepage](https://raw.githubusercontent.com/thinh-vu/vnstock/refs/heads/main/assets/images/vnstock-home-vi.png)](https://vnstocks.com/)

<div id="badges" align="center">
    <img src="https://img.shields.io/pypi/pyversions/vnstock?logoColor=brown&style=flat" alt="Version"/>
    <img src="https://img.shields.io/github/last-commit/thinh-vu/vnstock?style=flat" alt="Commit Badge"/>
    <img src="https://img.shields.io/badge/license-Custom%20License-red?style=flat" alt="Custom License Badge"/>
</div>

<div id="badges" align="center">
    <a href="https://pypi.org/project/vnstock/">
        <img src="https://img.shields.io/pypi/dm/vnstock?label=vnstock%20download&style=flat" alt="vnstock download badge"/>
    </a>
</div>

<div id="badges" align="center">
    <a href="https://vnstocks.com/insiders-program">
        <img src="https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86" alt="vnstock3 download badge"/>
    </a>
</div>
---

> ⚠️ **Note**: This document begins in 🇻🇳 Vietnamese for our local community.
>
> 🌐 **English version available below** — scroll or use the TOC (top-right 🟰) to navigate.

***

## Một thư viện Python để bạn tự truy xuất và chuẩn hoá dữ liệu chứng khoán Việt Nam

> Chào mừng bạn đến với **Vnstock**, thư viện Python có mã nguồn công khai giúp bạn tự truy xuất và chuẩn hoá **dữ liệu chứng khoán Việt Nam** từ các nguồn công khai mà bạn đã có quyền truy cập. Vnstock không sở hữu, không lưu trữ và không phân phối dữ liệu.

Dù bạn muốn dùng **vnstock python** để xây dựng mô hình định lượng, tích hợp vào nền tảng phân tích của mình hay chỉ để tìm hiểu **lịch sử giá cổ phiếu**, bạn đều có thể bắt đầu ngay hôm nay.

### Tại sao chọn Vnstock?

* **Miễn phí cho cá nhân, mã nguồn công khai**: Dễ dàng tiếp cận, phục vụ nhà đầu tư cá nhân và lập trình viên muốn truy xuất dữ liệu chứng khoán Việt Nam qua **vnstock**. Mã nguồn công khai để bạn đọc và kiểm chứng; điều kiện sử dụng theo [giấy phép](https://vnstocks.com/onboard/giay-phep-su-dung).
* **Giải quyết dữ liệu phân mảnh**: Không cần tự viết mã kết nối từng nguồn từ số 0. Bạn gọi một hàm, thư viện gửi yêu cầu từ chính kết nối mạng của bạn tới nguồn rồi chuẩn hoá kết quả về dạng DataFrame để bạn nối vào luồng phân tích hoặc lưu trữ.
* **Làm việc được với AI Agent**: Có sẵn tài liệu để trợ lý AI đọc và viết code dùng thư viện.

***

## Bắt đầu nhanh & Vibe Coding

Bạn không cần kiến thức sâu về code để sử dụng vnstock. Dự án có sẵn các hướng dẫn sau:

### 1. Trải nghiệm trực tiếp trên trình duyệt với Google Colab

Nếu bạn chỉ muốn thử nghiệm nhanh hoặc **chạy python online**, bạn có thể dùng Google Colab. Không cần thiết lập môi trường phức tạp!

[![Google Colab](https://img.shields.io/badge/Google_Colab-Xem_hướng_dẫn-F9AB00?style=for-the-badge\&logo=googlecolab\&logoColor=white)](https://vnstocks.com/onboard/trai-nghiem-vnstock?utm_source=github\&utm_medium=readme)

### 2. Vibe Coding với AI (Bạn Ra Lệnh, AI Làm)

Cách này phù hợp với cả người mới bắt đầu lẫn người đã quen việc. AI đọc tài liệu của thư viện để viết code, chạy chương trình và diễn giải kết quả — bạn vẫn nên kiểm tra lại trước khi dùng.

Để bắt đầu nhanh nhất, vui lòng tham khảo các hướng dẫn chi tiết sau:

* [![Vibe Coding Guide](https://img.shields.io/badge/Vibe_Coding-Xem_hướng_dẫn_nhanh-8B5CF6?style=for-the-badge\&logo=visualstudiocode\&logoColor=white)](https://vnstocks.com/onboard/vibe-coding)
* [![Agent Guide](https://img.shields.io/badge/Agent_Guide-Tài_liệu_chi_tiết-24292e?style=for-the-badge\&logo=gitbook\&logoColor=white)](https://vnstocks.com/onboard/agent-guide)
* [![Đăng ký API Key](https://img.shields.io/badge/vnstocks.com-Đăng_ký_API_Key-0066FF?style=for-the-badge\&logo=keycdn\&logoColor=white)](https://vnstocks.com/login)

***

## Cài đặt thư viện

Nếu bạn viết code thủ công, hãy cài đặt qua `pip`:

```bash
pip install -U vnstock
```

### Xác thực người dùng (API Key)

Thư viện tự giới hạn nhịp gọi để việc truy xuất không gây ảnh hưởng tới nguồn cấp công khai và tới cộng đồng người dùng. Mức giới hạn gắn với tài khoản:

* Khách (Guest): 20 lượt gọi/phút, không cần đăng ký
* Cộng đồng: 60 lượt gọi/phút, đăng ký miễn phí
* Tài trợ (Sponsor): 180–600 lượt gọi/phút

Tài trợ là khoản đóng góp cho dự án, đổi lại là giấy phép sử dụng bản mở rộng — không phải phí mua dữ liệu hay dung lượng truy vấn. Dữ liệu thuộc về nguồn công bố; điều kiện sử dụng của từng nguồn do bạn tự kiểm tra và tuân thủ.

```python
from vnstock import register_user
register_user() # Làm theo hướng dẫn trên terminal
```

***

## Giao diện Hợp nhất (Unified UI) - Vnstock v4+

Bạn không cần bận tâm hàm nào thuộc nguồn nào, chỉ cần tập trung vào nhóm dữ liệu.

```python
from vnstock import Market, Reference, Fundamental

market = Market()
ref = Reference()
fa = Fundamental()

# Lấy dữ liệu lịch sử giá cổ phiếu (OHLCV)
df_history = market.equity.ohlcv(symbol='VNM', start='2024-01-01', end='2024-05-01')

# Lấy thông tin hồ sơ doanh nghiệp tổng quan
df_profile = ref.company.info(symbol='FPT')

# Lấy báo cáo tài chính (Bảng cân đối kế toán) theo năm
df_balance = fa.equity.balance_sheet(symbol='TCB', period='year')
```

***

## Các nhóm dữ liệu Vnstock hỗ trợ

Các hàm truy xuất được chia thành 6 nhóm. Phạm vi dữ liệu phụ thuộc vào từng nguồn và có thể thay đổi:

1. **Dữ liệu Cổ phiếu (Equity):** Giá cổ phiếu trong phiên (có độ trễ theo nguồn cấp), **lịch sử giá cổ phiếu**, báo cáo tài chính, hồ sơ doanh nghiệp.
2. **Chỉ số thị trường (Index):** Biến động **lịch sử giá VNINDEX**, HNX, UPCOM và các chỉ số ngành.
3. **Chứng quyền (Warrant):** Thông tin chứng quyền, giá giao dịch, ngày đáo hạn, trạng thái giao dịch.
4. **Phái sinh (Futures):** Hợp đồng tương lai phái sinh VN30 và các kỳ hạn tương ứng.
5. **Quỹ đầu tư (Fund & ETF):** Thông tin danh mục, hiệu suất quỹ mở (FMarket) và các quỹ hoán đổi danh mục.
6. **Vĩ mô & Hàng hóa (Macro & Commodities):** Tỷ giá ngoại tệ (Forex), Giá vàng (SJC), Tiền điện tử (Crypto).

***

## Cấu trúc API (API Structure Tree)

Bạn có thể gọi hàm `show_api()` để in ra toàn bộ cấu trúc các hàm phục vụ cho việc lập chỉ mục AI hoặc tra cứu nhanh:

```text
API STRUCTURE TREE - VNSTOCK (Unified UI)
vnstock
├── Reference
│   ├── company # Access company-specific reference data.
│   │   ├── info() [KBS] -> DataFrame # Get company overview.
│   │   ├── shareholders() [KBS] -> DataFrame # List major shareholders.
│   │   ├── officers() [KBS] -> DataFrame # List company leadership.
│   │   ├── subsidiaries() [KBS] -> DataFrame # List subsidiaries.
│   │   ├── ownership() [KBS] -> DataFrame # Company ownership structure.
│   │   ├── insider_trading() [KBS] -> DataFrame # Insider trading history.
│   │   ├── capital_history() [KBS] -> DataFrame # Capital change history.
│   │   ├── news() [KBS] -> DataFrame # Company related news.
│   │   └── events() [KBS] -> DataFrame # Upcoming corporate events.
│   ├── equity # Equity symbols and grouping reference.
│   │   ├── list() [KBS] -> DataFrame # List all equity symbols.
│   │   ├── list_by_group() [KBS] -> DataFrame # List equities by group.
│   │   ├── list_by_industry() [VCI] -> DataFrame # List equities by industry.
│   │   └── list_by_exchange() [KBS] -> DataFrame # List symbols by exchange/board.
│   ├── index # Market index reference data.
│   │   ├── list() [KBS] -> DataFrame # List all market indices.
│   │   ├── members() [KBS] -> DataFrame # List constituents of an index.
│   │   ├── groups() [KBS] -> DataFrame # List supported index groups.
│   │   └── info() [KBS] -> DataFrame # Get all market indices metadata.
│   ├── etf # ETF reference data.
│   │   └── list() [KBS] -> DataFrame # List all trackers/ETFs.
│   ├── futures # Access index futures reference data.
│   │   ├── list() [KBS] -> DataFrame # List all futures instruments.
│   │   └── info() [KBS] -> Dict # Get futures specifications.
│   ├── warrant # Access covered warrant reference data.
│   │   ├── list() [KBS] -> DataFrame # List all covered warrants.
│   │   └── info() [KBS] -> Dict # Get warrant specifications.
│   ├── bond # Bond/Debt reference data.
│   │   └── list() # List all debt/bonds.
│   ├── fund # Mutual fund reference data.
│   │   ├── list() [FMarket] -> DataFrame # List all mutual funds.
│   │   ├── top_holding() [FMarket] -> DataFrame # Fund top holdings.
│   │   ├── industry_holding() [FMarket] -> DataFrame # Fund industry allocation.
│   │   ├── nav_report() [FMarket] -> DataFrame # Fund NAV performance.
│   │   └── asset_holding() [FMarket] -> DataFrame # Fund asset allocation.
│   ├── industry # Industry classification reference.
│   │   ├── list() [VCI] -> DataFrame # ICB industry classification.
│   │   └── sectors() [KBS] -> DataFrame # List symbols grouped by industry.
│   ├── market # Market status and metadata.
│   │   └── status() [KBS] -> Dict # Get live market status.
│   └── search # Search functionality.
│   │   ├── symbol() [MSN] -> DataFrame # Search for symbols globally.
│   │   └── info() [MSN] -> DataFrame # Search for detailed asset information.
├── Market
│   ├── quote() [KBS] -> DataFrame # Global in-session quote (source-delayed).
│   ├── equity # Access equity market data.
│   │   ├── ohlcv() [KBS] -> DataFrame # Historical OHLCV bars.
│   │   ├── quote() [KBS] -> DataFrame # In-session pricing board data (source-delayed).
│   │   └── trades() [KBS] -> DataFrame # Tick-by-tick trade tape.
│   ├── index # Access index market data.
│   │   └── ohlcv() [KBS] -> DataFrame # Historical OHLCV bars for indices.
│   ├── etf # Access ETF market data.
│   │   ├── ohlcv() [KBS] -> DataFrame # Historical OHLCV bars for ETFs.
│   │   ├── quote() [KBS] -> DataFrame # In-session pricing for ETFs (source-delayed).
│   │   └── trades() [KBS] -> DataFrame # Tick-by-tick trades for ETFs.
│   ├── futures # Access futures market data.
│   │   ├── ohlcv() [KBS] -> DataFrame # Historical OHLCV bars for Futures.
│   │   ├── quote() [KBS] -> DataFrame # In-session pricing for Futures (source-delayed).
│   │   └── trades() [KBS] -> DataFrame # Tick-by-tick trades for Futures.
│   ├── warrant # Access warrant market data.
│   │   ├── ohlcv() [KBS] -> DataFrame # Historical OHLCV bars for Warrants.
│   │   ├── quote() [KBS] -> DataFrame # In-session pricing for Warrants (source-delayed).
│   │   └── trades() [KBS] -> DataFrame # Tick-by-tick trades for Warrants.
│   ├── forex # Access forex market data.
│   │   └── ohlcv() [MSN] -> DataFrame # Historical OHLCV bars for forex.
│   ├── fund # Access Mutual Fund market data.
│   │   ├── history() [FMarket] -> DataFrame # Fund NAV history.
│   │   ├── nav() [FMarket] -> DataFrame # Fund NAV history.
│   │   ├── top_holding() [FMarket] -> DataFrame # Top holdings of the fund.
│   │   ├── industry_holding() [FMarket] -> DataFrame # Industry allocation of the fund.
│   │   └── asset_holding() [FMarket] -> DataFrame # Asset class allocation of the fund.
│   ├── commodity # Access commodity market data.
│   │   └── ohlcv() [MSN] -> DataFrame # Historical OHLCV for commodities.
│   └── crypto # Access crypto market data.
│   │   └── ohlcv() [MSN] -> DataFrame # Historical OHLCV for crypto.
├── Fundamental
│   └── equity # Access equity fundamental data.
│   │   ├── balance_sheet() [KBS] -> DataFrame # Get balance sheet.
│   │   ├── cash_flow() [KBS] -> DataFrame # Get cash flow.
│   │   ├── income_statement() [KBS] -> DataFrame # Get income statement.
│   │   └── ratios() [KBS] -> DataFrame # Financial ratios.
├── Retail
│   ├── gold() # Access gold price data.
│   └── exchange_rate() # Access exchange rate data.
```

***

## Hướng dẫn sử dụng chuyên sâu

Cách gọi hàm truyền thống riêng lẻ theo từng nguồn dữ liệu hiện không còn được khuyến nghị. Để sử dụng tài liệu hướng dẫn chuyên sâu cho AI Agent hoặc tự tuỳ biến chức năng, vui lòng tham khảo [Vnstock AI Agent Skills Hub](https://vnstocks.com/skill).

***

## Tuyên bố miễn trừ trách nhiệm

Dự án **Vnstock** là một công cụ có mã nguồn công khai giúp tự động hoá việc trích xuất dữ liệu từ các nguồn công khai, phục vụ **mục đích nghiên cứu và sử dụng cá nhân**. Vnstock **không phải là nhà cung cấp, không sở hữu hay kinh doanh dữ liệu**. Dữ liệu được trích xuất qua công cụ có thể không đầy đủ, không liên tục hoặc sai lệch so với nguồn gốc, do đó không khuyến nghị **sử dụng cho mục đích giao dịch thực tế, thuật toán đầu tư, hoặc ra quyết định tài chính** khi bạn không hiểu rõ.

Các tác giả **không chịu trách nhiệm đối với bất kỳ tổn thất hay thiệt hại nào**. Vnstock không cung cấp tư vấn đầu tư hay tín hiệu giao dịch.

**Không liên kết với các nguồn dữ liệu**: Vnstock **không có quan hệ liên kết, tài trợ hay chứng thực** với bất kỳ tổ chức nào được nhắc đến trong tài liệu hoặc mã nguồn. Mọi tên gọi, thương hiệu và nhãn hiệu được nêu chỉ nhằm mục đích chỉ dẫn nguồn gốc dữ liệu và thuộc về chủ sở hữu tương ứng. Người dùng chịu trách nhiệm tuân thủ điều khoản sử dụng của từng nguồn dữ liệu mà mình truy cập, cũng như sử dụng thư viện trong giới hạn hợp lý — truy xuất quá mức gây ảnh hưởng đến nguồn cấp công khai và tới chính cộng đồng người dùng.

**Dữ liệu ẩn danh**: Vnstock có thể ghi nhận dữ liệu ẩn danh về môi trường chạy nhằm cải thiện hiệu năng và độ ổn định của phần mềm. Chi tiết xem trong [giấy phép sử dụng](https://vnstocks.com/onboard/giay-phep-su-dung).

***

## Giấy phép sử dụng (License)

`Vnstock` được phát hành theo giấy phép tuỳ chỉnh, dành cho **mục đích cá nhân và phi thương mại**. Mã nguồn được công khai để bạn đọc, nghiên cứu và kiểm chứng, nhưng **đây không phải giấy phép nguồn mở theo chuẩn OSI**: việc phân phối lại và sử dụng cho mục đích thương mại cần có sự đồng ý bằng văn bản của tác giả. Xem [giấy phép](https://vnstocks.com/onboard/giay-phep-su-dung). Nếu bạn cần dùng cho dự án phát sinh doanh thu, vui lòng liên hệ tác giả để được cấp phép chính thức.

***

## Bạn đồng hành & Nhà tài trợ

Vnstock phát triển nhờ sự chung tay của cộng đồng những người yêu công nghệ và tài chính. Mỗi sự hỗ trợ (đóng góp code, đánh dấu yêu thích hay tài trợ) đều giúp dự án duy trì được máy chủ, bổ sung tính năng mới.

<div id="badges" align="center">
    <a href="https://vnstocks.com/insiders-program">
        <img src="https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86" alt="vnstock3 download badge"/>
    </a>
</div>

<a href="https://github.com/thinh-vu/vnstock/graphs/contributors">
   <img src="https://contributors-img.web.app/image?repo=thinh-vu/vnstock" width="800"/>
</a>

***

# Vnstock - The Source-Available Stock Analysis Toolkit for Investors

[![Vnstock Homepage](https://raw.githubusercontent.com/thinh-vu/vnstock/refs/heads/main/assets/images/vnstock-home-en.png)](https://vnstocks.com/)

<div id="badges" align="center">
    <img src="https://img.shields.io/pypi/pyversions/vnstock?logoColor=brown&style=flat" alt="Version"/>
    <img src="https://img.shields.io/github/last-commit/thinh-vu/vnstock?style=flat" alt="Commit Badge"/>
    <img src="https://img.shields.io/badge/license-Custom%20License-red?style=flat" alt="Custom License Badge"/>
</div>

## Introduction to Vnstock

Welcome to **Vnstock**, a source-available Python toolkit for retrieving and analysing Vietnamese stock market data.

Driven by the mission **"To make financial data extraction and investment tools accessible to everyone"**, Vnstock is maintained so you can build your own analysis tools in Python. Vnstock does not own, store or distribute any data.

### Why Vnstock?

* **Free for Personal Use, Source-Available**: An accessible data extraction tool for investors, analysts, researchers, and educators. The source is published so you can read and verify it; usage terms are set by the [licence](https://vnstocks.com/onboard/giay-phep-su-dung).
* **Full-Stack Python Support**: Easy-to-use functions for building research and analysis tools.
* **Unified Data Access**: Automate the retrieval of public data across stocks, warrants, indices, futures, bonds, forex and crypto through one interface. Coverage varies by source and may change. (Note: Vnstock is a retrieval tool, not a data provider).

### Join the Community

<div id="badges" align="center">
  <a href="https://www.facebook.com/groups/vnstock.official" target="_blank">
    <img src="https://img.shields.io/badge/Join%20the%20Community-Vnstock-blue?style=for-the-badge&logo=facebook" alt="Join Vnstock Community"/>
  </a>
</div>

## Installation

```bash
pip install -U vnstock
```

## Rate limits and account

The library paces its own requests so that retrieval does not burden the public sources or the user community. The limit is tied to your account:

* Guest: 20 calls/minute, no registration
* Community: 60 calls/minute, free registration
* Sponsor: 180–600 calls/minute

Sponsorship is a contribution to the project, returned as a licence to use the extended edition — it is not a fee for data or for query volume. The data belongs to the source that publishes it; you are responsible for checking and complying with each source's own terms.

```python
from vnstock import register_user
register_user()  # follow the instructions in your terminal
```

***

## Quick Start: Unified UI (Vnstock v4+)

Vnstock v4+ introduces the **Unified UI**, allowing you to fetch data without worrying about which source it comes from.

```python
from vnstock import Market, Reference, Fundamental

# Initialize data domains
market = Market()
ref = Reference()
fa = Fundamental()

# 1. Fetch historical stock prices (OHLCV)
df_history = market.equity.ohlcv(symbol='VNM', start='2024-01-01', end='2024-05-01')

# 2. Fetch general company profile
df_profile = ref.company.info(symbol='FPT')

# 3. Fetch financial data
df_balance = fa.equity.balance_sheet(symbol='TCB', period='year')
```

For more documentation and Vibe Coding guides, please refer to:

* [![Vibe Coding Guide](https://img.shields.io/badge/Vibe_Coding-Quick_Start_Guide-8B5CF6?style=for-the-badge\&logo=visualstudiocode\&logoColor=white)](https://vnstocks.com/onboard/vibe-coding)
* [![Agent Guide](https://img.shields.io/badge/Agent_Guide-Full_Documentation-24292e?style=for-the-badge\&logo=gitbook\&logoColor=white)](https://vnstocks.com/onboard/agent-guide)
* [![Get API Key](https://img.shields.io/badge/vnstocks.com-Get_Free_API_Key-0066FF?style=for-the-badge\&logo=keycdn\&logoColor=white)](https://vnstocks.com/login)

***

## Disclaimer

**Vnstock** is a source-available tool that automates the retrieval of publicly available data, intended for **research and personal use**. Vnstock **is not a data provider and does not own or resell any data**. Data retrieved through this tool may be incomplete, discontinuous, or inconsistent with its origin, and is therefore **not recommended for live trading, algorithmic investing, or financial decision-making** unless you fully understand its limitations.

The authors **accept no liability for any loss or damage**. Vnstock does not provide investment advice or trading signals.

**No affiliation with data sources**: Vnstock is **not affiliated with, sponsored by, or endorsed by** any organisation referenced in this documentation or in the source code. All names, brands and trademarks mentioned are used solely to indicate the origin of data and remain the property of their respective owners. Users are responsible for complying with the terms of service of any data source they access, and for using this library within reasonable limits — excessive retrieval harms public data sources and the user community alike.

**Anonymous data**: Vnstock may record anonymous information about the runtime environment in order to improve software performance and stability. See the [licence](https://vnstocks.com/onboard/giay-phep-su-dung) for details.

***

## Licence

`Vnstock` is released under a custom licence for **personal, non-commercial use**. It is **not an OSI-approved open-source licence**: redistribution and commercial use are not permitted without prior written consent. See the [licence](https://vnstocks.com/onboard/giay-phep-su-dung). If you need it for a revenue-generating project, please contact the author for formal licensing.
