# Vnstock - Bộ Công Cụ Python Cho Thị Trường Chứng Khoán Việt Nam

[![Vnstock Homepage](https://raw.githubusercontent.com/thinh-vu/vnstock/refs/heads/main/assets/images/vnstock-home-vi.png)](https://vnstocks.com/)

<div id="badges" align="center">
    <a href="https://vnstocks.com/download">
        <img src="https://img.shields.io/badge/packages-vnstocks.com-0066FF?logo=python&logoColor=white&style=flat" alt="Vnstock Packages"/>
    </a>
    <img src="https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white&style=flat" alt="Python 3.10+"/>
    <img src="https://img.shields.io/github/last-commit/thinh-vu/vnstock?style=flat" alt="Commit Badge"/>
    <img src="https://img.shields.io/badge/license-Custom%20License-red?style=flat" alt="Custom License Badge"/>
    <a href="https://vnstocks.com/insiders-program">
        <img src="https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86" alt="Sponsor"/>
    </a>
</div>
---

> 🚀 **Vnstock Thế hệ 5**: Phiên bản thế hệ 5 được tái thiết kế với kiến trúc **nhân xử lý [Rust](https://rust-lang.org/)** và **tầng giao diện Python**, mang lại tốc độ cài đặt và hiệu năng truy xuất vượt trội so với các bản thuần Python trước đây.
>
> 📌 **Lưu ý về Repository này**: Mã nguồn trong kho lưu trữ GitHub này đại diện cho phiên bản **Vnstock 4.x** (lưu trữ phục vụ tham khảo lịch sử). Toàn bộ hệ sinh thái thế hệ 5 được phát hành dưới dạng gói biên dịch sẵn qua [trang quản lý gói chính thức](https://vnstocks.com/download) (bản Cộng đồng miễn phí cho cá nhân, học tập và nghiên cứu). Chi tiết xem tại [vnstocks.com/the-he-5](https://vnstocks.com/the-he-5) và [tài liệu chính thức](https://vnstocks.com/docs).

> ⚠️ **Note**: This document begins in 🇻🇳 Vietnamese for our local community.
>
> 🌐 **English version available below** — scroll or use the TOC (top-right 🟰) to navigate.

***

## Thư viện Python để bạn tự kết nối và chuẩn hoá dữ liệu thị trường tài chính Việt Nam

> Chào mừng bạn đến với **Vnstock**, hệ sinh thái tự động hoá cá nhân trong nghiên cứu đầu tư: bộ công cụ Python giúp bạn tự kết nối, chuẩn hoá và phân tích dữ liệu thị trường tài chính Việt Nam từ nguồn bên thứ ba, chạy trên hạ tầng do bạn kiểm soát. Vnstock cấp quyền sử dụng phần mềm cho cá nhân, không cấp quyền sử dụng dữ liệu của nguồn và không vận hành kho dữ liệu thị trường để bán lại.

Dù bạn muốn dùng `vnstock` để tự động hoá quy trình phân tích, xây dựng mô hình nghiên cứu định lượng hay tìm hiểu lịch sử dữ liệu thị trường, bạn đều có thể bắt đầu ngay hôm nay.

### Tại sao chọn Vnstock?

* **Bản Cộng đồng miễn phí cho cá nhân, học tập và nghiên cứu**: Dễ dàng tiếp cận, phục vụ cá nhân nghiên cứu và người thích khám phá công nghệ muốn tự kết nối dữ liệu thị trường qua thư viện `vnstock`. Điều kiện sử dụng theo [giấy phép](https://vnstocks.com/onboard/giay-phep-su-dung).
* **Giải quyết dữ liệu phân mảnh**: Không cần tự viết mã kết nối từng nguồn từ số 0. Bạn gọi một hàm, thư viện gửi yêu cầu từ chính kết nối mạng của bạn tới nguồn rồi chuẩn hoá kết quả về dạng DataFrame để bạn nối vào luồng phân tích hoặc lưu trữ.
* **Tối ưu cho tác nhân AI**: Có sẵn tài liệu để tác nhân AI hiểu đúng cú pháp và viết code chính xác ngay lần đầu.

***

## Bắt đầu nhanh & Vibe Coding

Bạn không cần biết lập trình trước để bắt đầu với Vnstock. Dự án có sẵn các hướng dẫn sau:

### 1. Trải nghiệm trực tiếp trên trình duyệt với Google Colab

Nếu bạn muốn thử nghiệm nhanh hoặc chạy Python trên trình duyệt, bạn có thể dùng Google Colab mà không cần cài đặt môi trường trên máy tính.

[![Google Colab](https://img.shields.io/badge/Google_Colab-Xem_hướng_dẫn-F9AB00?style=for-the-badge\&logo=googlecolab\&logoColor=white)](https://vnstocks.com/onboard/trai-nghiem-vnstock?utm_source=github\&utm_medium=readme)

### 2. Làm việc với tác nhân AI (AI Agent)

Bạn có hai cách tiếp cận linh hoạt để kết hợp Vnstock cùng tác nhân AI:

* **Tùy chọn 1: Vibe Coding với Agent Guide**
  Bạn mô tả ý tưởng phân tích bằng ngôn ngữ tự nhiên trong các IDE hỗ trợ như (Antigravity IDE, VS Code, Cursor, ...). Tác nhân AI đọc tài liệu chuẩn (`AGENTS.md` / Agent Guide) của thư viện để tự động viết code và chạy thử nghiệm. Bạn tự kiểm chứng lại kết quả trước khi đưa vào luồng nghiên cứu chính thức.
  * Hướng dẫn nhanh: [Vibe Coding Guide](https://vnstocks.com/onboard/vibe-coding)
  * Hướng dẫn khởi tạo: [Onboarding Agent Guide](https://vnstocks.com/onboard/agent-guide)

* **Tùy chọn 2: Kết nối trực tiếp vào giao diện Chat qua `vnstock-mcp`**
  Sử dụng giao thức Model Context Protocol thông qua gói `vnstock_mcp`. Gói MCP chạy cục bộ bằng Python trên máy tính của bạn, hoạt động như một cầu nối (connector) cho phép tác nhân AI trong các giao diện trò chuyện (Claude, ChatGPT, Gemini Spark, v.v.) trực tiếp gọi các công cụ truy xuất của Vnstock theo ngữ cảnh hội thoại.
  * Trang giới thiệu: [vnstocks.com/vnstock-mcp](https://vnstocks.com/vnstock-mcp)
  * Tài liệu cấu hình chi tiết: [Tài liệu vnstock-mcp](https://vnstocks.com/docs/vnstock-mcp)

* [![Vibe Coding Guide](https://img.shields.io/badge/Vibe_Coding-Xem_hướng_dẫn_nhanh-8B5CF6?style=for-the-badge\&logo=visualstudiocode\&logoColor=white)](https://vnstocks.com/onboard/vibe-coding)
* [![Agent Guide](https://img.shields.io/badge/Agent_Guide-Tài_liệu_chi_tiết-24292e?style=for-the-badge\&logo=gitbook\&logoColor=white)](https://vnstocks.com/onboard/agent-guide)
* [![vnstock-mcp](https://img.shields.io/badge/vnstock--mcp-Tài_liệu_kết_nối-0066FF?style=for-the-badge\&logo=anthropic\&logoColor=white)](https://vnstocks.com/docs/vnstock-mcp)
* [![Lấy API Key](https://img.shields.io/badge/vnstocks.com-Lấy_API_Key-10B981?style=for-the-badge\&logo=keycdn\&logoColor=white)](https://vnstocks.com/download)

#### Tự động nạp Agent Skills & Tài liệu (Thế hệ 5)

Ở Thế hệ 5, tác nhân AI tự động tải động kỹ năng và tài liệu hướng dẫn trực tiếp từ máy chủ Vnstock thông qua chính thư viện `vnstock` mà không cần cài thêm `vnai`. Thư viện **không tự ý ghi đè tệp tĩnh hay can thiệp cấu hình hệ thống** trên máy bạn.

Tác nhân AI có thể tra cứu danh mục kỹ năng và nạp nội dung kỹ năng vào ngữ cảnh:

```python
from vnstock.utils.agents import load_skill, load_skill_catalog

# Xem danh mục kỹ năng theo cấp tài khoản
catalog = load_skill_catalog()

# Nạp động kỹ năng vào ngữ cảnh AI (ví dụ: vnstock-bootstrap)
skill_code = load_skill("vnstock-bootstrap")
```

Chi tiết cơ chế phân quyền, danh mục kỹ năng và tài liệu hướng dẫn đầy đủ xem tại [Tự động nạp Agent Skills và tài liệu](https://vnstocks.com/docs/tai-lieu/vnstock-agent-skills).

***

## Cài đặt thư viện thế hệ 5

Hệ sinh thái Vnstock thế hệ 5 được phân phối qua [trang quản lý gói chính thức](https://vnstocks.com/download) trên website (cài đặt qua kho gói `https://vnstocks.com/api/packages`). Xem giới thiệu chi tiết về các cải tiến tại [trang Thế hệ 5](https://vnstocks.com/the-he-5) và tra cứu [tài liệu chính thức](https://vnstocks.com/docs).

Cài đặt đồng thời thư viện cốt lõi `vnstock`, bộ công cụ tính toán định lượng `vnstock_quant` và giao thức MCP chạy cục bộ `vnstock_mcp` (đều có bản Cộng đồng miễn phí cho cá nhân, học tập và nghiên cứu):

```bash
pip install -U --extra-index-url https://vnstocks.com/api/packages vnstock vnstock_quant vnstock_mcp
```

> 💡 **Khuyên dùng:** Luôn cài đặt vào một môi trường ảo cố định (`~/.venv` trên macOS/Linux hoặc `$HOME\.venv` trên Windows) để tránh xung đột với các phiên bản cũ và dễ dàng tích hợp với trợ lý AI.

### Đăng nhập tài khoản & Kiểm tra trạng thái

Mỗi máy chỉ cần đăng nhập một lần bằng công cụ dòng lệnh tích hợp sẵn. Lấy khoá API tại [trang tải Vnstock](https://vnstocks.com/download) (kèm câu lệnh có sẵn khoá để bạn sao chép và kết nối tài khoản nhanh chóng):

```bash
# Đăng nhập bằng khoá API (nhập ẩn an toàn trên terminal)
vnstock register

# Xem cấp tài trợ, hạn dùng và trạng thái các thư viện đã cài
vnstock status
```

Nếu tham gia chương trình **Vnstock Sponsor**, bạn có thể tải thêm các thư viện thuộc bản Mở rộng (`vnstock_news`, `vnstock_pipeline`) theo cấp tài trợ của tài khoản:

```bash
vnstock install            # Cài đặt toàn bộ thư viện mở rộng được phân quyền
vnstock install -U         # Cập nhật tất cả thư viện đã cài lên bản mới nhất
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

## Khả năng truy xuất dữ liệu của thư viện Vnstock

Khi sử dụng `vnstock` như một công cụ Python trên máy cá nhân, thư viện cung cấp các hàm hỗ trợ kết nối và trích xuất dữ liệu từ các nguồn công bố bên thứ ba theo 6 nhóm chức năng (phạm vi dữ liệu phụ thuộc vào từng nguồn tương ứng và có thể thay đổi; Vnstock là công cụ trích xuất dữ liệu, không cung cấp dữ liệu như một dịch vụ và không kinh doanh dữ liệu):

1. **Dữ liệu Cổ phiếu (Equity):** Giá trong phiên (có độ trễ theo nguồn cấp), **lịch sử giá cổ phiếu**, báo cáo tài chính, hồ sơ doanh nghiệp.
2. **Chỉ số thị trường (Index):** Biến động **lịch sử chỉ số VNINDEX**, HNX, UPCOM và các chỉ số ngành.
3. **Chứng quyền (Warrant):** Thông tin chứng quyền, thị giá, ngày đáo hạn.
4. **Phái sinh (Futures):** Hợp đồng tương lai chỉ số VN30 và các kỳ hạn tương ứng.
5. **Quỹ đầu tư (Fund & ETF):** Thông tin danh mục, hiệu suất quỹ mở và các quỹ hoán đổi danh mục.
6. **Vĩ mô & Hàng hóa (Macro & Commodities):** Tỷ giá ngoại tệ (Forex), giá vàng, tiền mã hoá (Crypto).

***

## Cấu trúc API (API Structure Tree)

Bạn có thể gọi hàm `show_api()` để in ra toàn bộ cấu trúc các hàm phục vụ cho việc lập chỉ mục AI hoặc tra cứu nhanh:

```text
API STRUCTURE TREE - Vnstock (Unified UI)
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

Vnstock là hệ sinh thái công cụ Python giúp bạn tự kết nối và chuẩn hoá dữ liệu từ nguồn bên thứ ba, phục vụ **mục đích nghiên cứu và tham khảo**. Thư viện phát hành theo giấy phép riêng của Vnstock. Vnstock **không phải nhà cung cấp dữ liệu** và không vận hành kho dữ liệu thị trường tập trung để bán lại. Dữ liệu từ nguồn có thể không đầy đủ, không liên tục, bị trùng, sai lệch hoặc làm tròn; bạn cần tự đối chiếu với nguồn chính thức trước khi đưa vào phân tích hoặc công bố.

Phần mềm được cung cấp theo hiện trạng và theo khả năng sẵn có. Trong phạm vi pháp luật cho phép, Vnstock và tác giả không chịu trách nhiệm đối với tổn thất gián tiếp, ngẫu nhiên, đặc biệt hoặc hệ quả, bao gồm việc gián đoạn nghiên cứu hay mất mát dữ liệu. Vnstock không cung cấp tư vấn đầu tư hay khuyến nghị mua bán. Xem đầy đủ tại [Tuyên bố miễn trừ trách nhiệm](https://vnstocks.com/onboard/mien-tru-trach-nhiem).

**Không liên kết với các nguồn dữ liệu**: Vnstock **không có quan hệ liên kết, tài trợ hay chứng thực** với bất kỳ tổ chức nào được nhắc đến trong tài liệu hoặc phần mềm. Mọi tên gọi, thương hiệu và nhãn hiệu được nêu chỉ nhằm chỉ dẫn nguồn gốc dữ liệu và thuộc về chủ sở hữu tương ứng. Nguồn bên thứ ba gồm cả nguồn truy cập công khai và nguồn yêu cầu tài khoản hoặc quyền truy cập riêng; tình trạng có thể truy cập không đồng nghĩa quyền sử dụng không giới hạn. Bạn có trách nhiệm tự kiểm tra và tuân thủ các quy định pháp luật hiện hành cũng như điều kiện sử dụng của từng nguồn dữ liệu, đồng thời sử dụng thư viện trong giới hạn tần suất hợp lý nhằm tuân thủ quy định và tránh gây ảnh hưởng tới hạ tầng nguồn cấp hay cộng đồng người dùng.

**Dữ liệu và quyền riêng tư**: Truy vấn, xử lý và lưu trữ nghiệp vụ diễn ra trên hạ tầng do bạn lựa chọn. Các dịch vụ do Vnstock vận hành xử lý dữ liệu tài khoản, thanh toán, giấy phép, thiết bị, hạn mức, bảo mật và đo lường kỹ thuật theo [Chính sách quyền riêng tư](https://vnstocks.com/onboard/chinh-sach-quyen-rieng-tu).

***

## Giấy phép sử dụng (License)

Vnstock là công cụ tự động hoá cá nhân và cấp quyền sử dụng phần mềm cho cá nhân. Thư viện phát hành theo giấy phép riêng của Vnstock: **bản Cộng đồng miễn phí cho cá nhân, học tập và nghiên cứu**. Đây **không phải giấy phép nguồn mở theo chuẩn OSI**. Từ thế hệ 5, phần mềm được phát hành dưới dạng đóng gói sẵn.

Phạm vi sử dụng được tính theo số người dùng, số thiết bị đã đăng ký và hạn mức của từng cấp tài trợ, không phân biệt theo tính chất công việc — trong phạm vi đó bạn được dùng cho cả công việc của chính mình, kể cả việc có thu nhập. Hai trường hợp luôn cần thoả thuận riêng bằng văn bản: phân phối lại phần mềm, và làm sản phẩm mà giá trị chính là cấp cho bên thứ ba khả năng truy xuất dữ liệu. Bản có hiệu lực: [Giấy phép sử dụng](https://vnstocks.com/onboard/giay-phep-su-dung) (license-2026.09).

**Văn bản pháp lý**: [Giấy phép sử dụng](https://vnstocks.com/onboard/giay-phep-su-dung) · [Chính sách quyền riêng tư](https://vnstocks.com/onboard/chinh-sach-quyen-rieng-tu) · [Tuyên bố miễn trừ trách nhiệm](https://vnstocks.com/onboard/mien-tru-trach-nhiem)

***

## Đồng hành & Tài trợ dự án

Vnstock phát triển nhờ sự chung tay của cộng đồng những người yêu công nghệ và tự động hoá. Mỗi sự đồng hành (chia sẻ kinh nghiệm, đánh dấu sao yêu thích hay tài trợ) đều giúp dự án duy trì hạ tầng kỹ thuật và phát triển thêm các công cụ định lượng mới.

<div id="badges" align="center">
    <a href="https://vnstocks.com/insiders-program">
        <img src="https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86" alt="vnstock3 download badge"/>
    </a>
</div>

<a href="https://github.com/thinh-vu/vnstock/graphs/contributors">
   <img src="https://contributors-img.web.app/image?repo=thinh-vu/vnstock" width="800"/>
</a>

***

# Vnstock - Python Toolkit for Vietnam Financial Markets

[![Vnstock Homepage](https://raw.githubusercontent.com/thinh-vu/vnstock/refs/heads/main/assets/images/vnstock-home-en.png)](https://vnstocks.com/)

<div id="badges" align="center">
    <a href="https://vnstocks.com/download">
        <img src="https://img.shields.io/badge/packages-vnstocks.com-0066FF?logo=python&logoColor=white&style=flat" alt="Vnstock Packages"/>
    </a>
    <img src="https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white&style=flat" alt="Python 3.10+"/>
    <img src="https://img.shields.io/github/last-commit/thinh-vu/vnstock?style=flat" alt="Commit Badge"/>
    <img src="https://img.shields.io/badge/license-Custom%20License-red?style=flat" alt="Custom License Badge"/>
    <a href="https://vnstocks.com/insiders-program">
        <img src="https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86" alt="Sponsor"/>
    </a>
</div>

> 🚀 **Vnstock Generation 5**: The 5th generation has been completely re-engineered with a **high-performance Rust core** and a sleek **Python interface layer**, delivering vastly improved installation speed and runtime efficiency compared to legacy pure-Python versions.
>
> 📌 **Repository Notice**: The source code in this GitHub repository represents the legacy **Vnstock 4.x** codebase (preserved for historical reference). The Generation 5 ecosystem is distributed as pre-compiled packages via the [official package manager](https://vnstocks.com/download) (with a free Community edition for personal, educational, and research use). Learn more at [vnstocks.com/the-he-5](https://vnstocks.com/the-he-5) and read the [official documentation](https://vnstocks.com/docs).

## Introduction to Vnstock

Welcome to **Vnstock**, an ecosystem of Python tools for financial-market data and research workflows in Vietnam: connectors and normalization for third-party sources, technical indicators, news processing, data pipelines and guides for AI agents. The software runs on infrastructure you control; market queries go straight from there to the source. Vnstock licenses software to individuals, does not license source data, and does not operate a centralized market-data store for resale.

### Why Vnstock?

* **Free Community Edition for Personal, Study and Research Use**: An accessible tool for individual researchers and developers to connect to market data. Usage terms are defined in the [licence](https://vnstocks.com/onboard/giay-phep-su-dung).
* **Built for Independent Research**: Straightforward Python functions for building automated analysis and research workflows.
* **Unified Interface**: Connect to stocks, indices, warrants, futures, and funds through one consistent interface. Queries go directly from your machine to third-party sources. (Note: Vnstock is a client-side tool, not a data provider).

### Join the Community

<div id="badges" align="center">
  <a href="https://www.facebook.com/groups/vnstock.official" target="_blank">
    <img src="https://img.shields.io/badge/Join%20the%20Community-Vnstock-blue?style=for-the-badge&logo=facebook" alt="Join Vnstock Community"/>
  </a>
</div>

## Installation (Generation 5)

The Vnstock Generation 5 ecosystem is distributed via the [official package management page](https://vnstocks.com/download) on the website (installed via package index `https://vnstocks.com/api/packages`). Explore new features on the [Generation 5 page](https://vnstocks.com/the-he-5) and read the [official documentation](https://vnstocks.com/docs).

Install the core library `vnstock`, quantitative analysis tools `vnstock_quant`, and local MCP protocol package `vnstock_mcp` (all include a free Community edition for personal, educational, and research use):

```bash
pip install -U --extra-index-url https://vnstocks.com/api/packages vnstock vnstock_quant vnstock_mcp
```

> 💡 **Recommendation:** Install into a dedicated virtual environment (`~/.venv` on macOS/Linux or `$HOME\.venv` on Windows) to prevent conflicts with legacy releases.

### Account Login & Status Check

Log in once per machine using the built-in CLI tool. Retrieve your API key at [vnstocks.com/download](https://vnstocks.com/download) (which provides a ready-to-copy command with your key):

```bash
# Log in with your API key (typed securely at a hidden prompt)
vnstock register

# Check sponsor tier, validity, and installed libraries
vnstock status
```

If you participate in the **Vnstock Sponsor** program, install the add-on libraries from the Extended edition (`vnstock_news`, `vnstock_pipeline`) according to your tier:

```bash
vnstock install            # Install all entitled add-on libraries
vnstock install -U         # Update installed libraries to the latest release
```

***

### Vnstock Agent Skills for AI Assistants (Generation 5)

In Generation 5, AI agents dynamically load skills and documentation directly via the `vnstock` library without needing extra packages like `vnai`. The library **never writes to local files or modifies system configurations**.

AI agents can inspect available skills and load dynamic guidance into their context:

```python
from vnstock.utils.agents import load_skill, load_skill_catalog

# List available skills based on your account tier
catalog = load_skill_catalog()

# Dynamically load a skill into AI context (e.g., vnstock-bootstrap)
skill_code = load_skill("vnstock-bootstrap")
```

For detailed documentation, permissions, and skill catalogs, visit [Dynamic Loading for Agent Skills](https://vnstocks.com/docs/tai-lieu/vnstock-agent-skills).

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
* [![vnstock-mcp](https://img.shields.io/badge/vnstock--mcp-Connector_Docs-0066FF?style=for-the-badge\&logo=anthropic\&logoColor=white)](https://vnstocks.com/docs/vnstock-mcp)
* [![Get API Key](https://img.shields.io/badge/vnstocks.com-Get_API_Key-10B981?style=for-the-badge\&logo=keycdn\&logoColor=white)](https://vnstocks.com/download)

***

## Disclaimer

**Vnstock** is a personal-automation Python toolkit that helps you connect to and normalize data from third-party sources, intended for **research and reference**. Distributed under Vnstock's own licence, Vnstock **is not a data provider** and does not operate a centralized market-data store for resale. Source data may be incomplete, discontinuous, duplicated, inaccurate or rounded; verify against official sources before analysis or publishing.

The software is provided as-is and as-available. To the extent permitted by law, Vnstock and the author are not liable for indirect, incidental, special or consequential loss, including lost profit or research disruption. Vnstock does not provide investment advice or trade recommendations. See the full [Disclaimer](https://vnstocks.com/onboard/mien-tru-trach-nhiem).

**No affiliation with data sources**: Vnstock is **not affiliated with, sponsored by, or endorsed by** any organisation referenced in this documentation or in the software. All names, brands and trademarks mentioned are used solely to indicate the origin of data and remain the property of their respective owners. Third-party sources include both publicly accessible ones and ones requiring an account or private access; being reachable does not imply unlimited rights of use. You are responsible for complying with applicable laws and the terms of each third-party source, and using the library within reasonable rate limits to ensure compliance and avoid burdening public sources or the user community.

**Data and privacy**: Business queries, processing and storage happen on infrastructure you choose. Vnstock-operated services process account, payment, licence, device, quota, security and telemetry data per the [Privacy Policy](https://vnstocks.com/onboard/chinh-sach-quyen-rieng-tu).

***

## Licence

Vnstock is personal-automation software licensed to individuals. The Community edition is free under Vnstock's own licence, for **personal use, study and research only**. It is **not an OSI-approved open-source licence**. From Generation 5 onward, software is distributed as pre-packaged binaries.

Scope is measured by number of users, registered devices and the sponsor tier's quota — not by purpose; within that scope you may use Vnstock for your own work, including paid work. Two things always need a separate written agreement: redistributing the software, and operating a product whose primary value is giving third parties access to market data. Effective version: [Licence](https://vnstocks.com/onboard/giay-phep-su-dung) (license-2026.09).

**Legal**: [Licence](https://vnstocks.com/onboard/giay-phep-su-dung) · [Privacy Policy](https://vnstocks.com/onboard/chinh-sach-quyen-rieng-tu) · [Disclaimer](https://vnstocks.com/onboard/mien-tru-trach-nhiem)
