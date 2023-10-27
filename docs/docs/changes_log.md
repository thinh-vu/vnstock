---
sidebar_position: 7
---

# Lịch sử cập nhật

## 27-10-2023
- Bổ sung và hoàn thiện một số hàm cho vnstock
  - Hàm `listing_companies` nay được cung cấp thêm khả năng lấy danh sách công ty niêm yết từ SSI/FiinTrade. Việc này giúp người dùng có thể tham chiếu mã công ty từ mã cổ phiếu để lấy thông tin trong một số trường hợp đặc biệt FiinTrade sử dụng mã này thay cho mã cổ phiếu. Ví dụ, thay vì dùng mã cổ phiếu `BCM` gây ra lỗi cho hàm, bạn cần sử dụng mã công ty tương ứng là `BIDC`
  - Hàm `indices_listing` cho phép liệt kê tất cả mã chỉ số hiện có trên sàn.
  - Hàm `financial_ratio_compare` cho phép so sánh chỉ số tài chính của một danh sách các mã cổ phiếu.

## 26-10-2023
- Khôi phục các hàm lấy dữ liệu từ nguồn SSI gồm `financial_report`, `fr_trade_heatmap`, `market_top_mover` do SSI hiện tại đã gỡ bỏ mọi hạn chế về kỹ thuật áp dụng cho bot thực hiện web scraping.
- Cập nhật tài liệu sử dụng kèm theo
- Cập nhật Demo Notebook

## 25-10-2023
- Bổ sung hướng dẫn xuất dữ liệu sang các định dạng phổ biến bao gồm CSV, Excel, và dữ liệu cho Amibroker.
- Thử nghiệm tính năng Blog của Mkdocs Matterial cho chuyên mục Kiến thức.

## 21-10-2023
- Giới thiệu cách sử dụng vnstock trong Google Sheets với Neptyne for Google Sheets.
- Di chuyển mục nội dung vnstock cho Google Sheets sang tab `Ứng dụng & Tích hợp`

## 20-10-2023
- Chuyển đổi nền tảng tài liệu từ Pretty-Docs sang [MkDocs Matterial](https://squidfunk.github.io/mkdocs-material/) thân thiện và nhiều tính năng hữu ích hơn.

- Cập  nhật mô tả các hàm để tiện theo dõi bao gồm:
    - Xoay DataFrame kết quả trả về để có thể hiển thị đầy đủ tên các cột dữ liệu
    - Bổ sung mô tả tham số đầu vào của hàm

## 14-10-2023

> Phiên bản: 0.2.2: Đưa tính năng vẽ đồ thị chính thức vào phiên bản ổn định, cập nhật hàm truy xuất giá lịch sử

- Cập nhật hàm `stock_historical_data` để trả về thông tin chính xác
    - Loại bỏ bước tính toán nhân chỉ số và mã phái sinh với 1000 khi trả về dữ liệu. Cách tính này làm sai lệch giá trị của chỉ số và mã phái sinh vì bản chất giá trị OHLC này khác với giá cổ phiếu.
    - Bổ sung thêm tham số **beautify**, đặt giá trị mặc định là True để giữ nguyên cách nhân 1000 cho giá cổ phiếu. Người dùng có thể chuyển về False để giữ nguyên giá trị OHLC dạng thập phân rút gọn.

- Chính thức đưa các hàm vẽ đồ thị vào phiên bản chính thức của vnstock sau quá trình thử nghiệm
    - Hàm **candlestick_chart** cho phép vẽ đồ thị nến cùng các đường trung bình động, hỗ trợ, kháng cự cơ bản.
    
    ![candlestick](assets/images/VIC_candlestick.png?raw=true)

    - Hàm **bollinger_bands_chart** cho phép vẽ đồ thị nến (hoặc đường) kèm các dải Bollinger Bands. Hàm này cần sử dụng kèm hàm **bollinger_bands** để chuyển đổi dữ liệu OHLC tiêu chuẩn sang dữ liệu Bollinger Bands.

    ![bollinger bands](assets/images/bollinger_bands_chart.png?raw=true)

## 10-10-2023

- Hàm **listing_company** được điều chỉnh để hỗ trợ truy xuất danh sách mã cổ phiếu cập nhật realtime qua API.
    - Bổ sung tham số **live** nhận giá trị True hoặc False, mặc định là False cho phép truy xuất danh sách cổ phiếu từ tệp csv lưu trữ trên Github. Cấu trúc của file dữ liệu cục bộ chứa thông tin đầy đủ hơn so với chế độ realtime.
    - Loại bỏ tham số **path**

## 06-10-2023

> Thay đổi cấu trúc thư mục và tài liệu vnstock repo trên Github

- Tái cấu trúc cây thư mục của vnstock repo trên Github
  - Chuyển toàn bộ file markdown vào thư mục **docs** trừ file README (Tiếng Việt).
    - Chuyển thư mục **src** vào bên trong thư mục **docs** và đổi tên thành **resources**. Các file ảnh đính kèm dự án được đưa vào sâu hơn 1 cấp bên trong thư mục **images**.
  - Đơn giản hóa nội dung file README của repo. Đưa tất cả tài liệu hướng dẫn vào vnstock docs.
  - Bổ sung cơ chế kiểm tra mã phản hồi (status_code) của API trước khi trả về dữ liệu cho hàm **stock_intraday_data**

## 05-10-2023

> vnstock docs Phiên bản 1.1 sử dụng Pretty-Docs theme

Thử nghiệm thành công và ra mắt phiên bản thử nghiệm 1.0 cho trang tài liệu vnstock docs sử dụng pretty-docs theme.

## 22-08-2023
- Cập nhật tệp dữ liệu **listing_companies** lên phiên bản mới nhất.
- Cập nhật hàm **financial flow**
  - Thêm tham số **get_all** để lấy tất cả dữ liệu có sẵn hoặc chỉ dữ liệu mới nhất (5 năm hoặc 10 quý).
- Cập nhật Demo Notebook để minh họa các thay đổi mới nhất.

## 24-07-2023
- Bắt đầu triển khai hàm truy xuất dữ liệu chứng khoán phái sinh.
- Kết hợp một hàm sàng lọc cổ phiếu từ TCBS vào thư viện.
- Cải thiện hàm stock_historical_data với các cập nhật sau:
  - Khi độ khung thời gian (resolution) được đặt thành **1D**, cột thời gian sẽ hiển thị theo định dạng ngày **YYYY-mm-dd**.
  - Thêm một giá trị mới **derivative** cho tham số **type**, cho phép truy xuất dữ liệu phái sinh.
- Các tham chiếu hàm trong tệp README đã được cấu trúc theo các tình huống sử dụng thực tế, như Phân tích Kỹ thuật, Phân tích Cơ bản, Sàng lọc Cổ phiếu, vv. Điều này giúp cho tài liệu thân thiện và có tổ chức hơn với người dùng. Phiên bản tiếng Anh của tệp README cũng đã được cập nhật để phù hợp với phiên bản tiếng Việt.

### 22-07-2023
- Bổ sung hướng dẫn vào [Demo Notebook](https://github.com/thinh-vu/vnstock/blob/beta/demo/gen2_vnstock_demo_index_all_functions_testing_2023.ipynb) giúp người dùng xuất dữ liệu từ Google Colab ra Google Sheets.

### 14-07-2023
- Phát hành phiên bản 0.17 trên PyPI.
- Những thay đổi trên nhánh **beta** sẽ được cập nhật vào nhánh **main** và phát hành qua PyPI hàng tháng từ bây giờ.
- File README.md đã được cập nhật để đồng bộ hóa phiên bản tiếng Anh và tiếng Việt.
- Dữ liệu file listing_companies_enhanced-2023.csv trong thư mục data của repo này được sử dụng để cung cấp dữ liệu công ty niêm yết cho hàm listing_companies.
- Hàm mới, price_depth, đã được giới thiệu để lấy giá và khối lượng giao dịch cho danh sách các cổ phiếu. Hàm này có thể được sử dụng song song với hàm price_board.

### 13-07-2023
- Phân loại các tính năng của vnstock trong file Demo Jupyter Notebook theo 5 nhóm chính:
  1. Thị trường (Market Watch)
  2. Phân tích cơ bản (Fundamental Analysis)
  3. Phân tích kỹ thuật (Technical Analysis)
  4. Lựa chọn cổ phiếu (Stock Screening)
  5. Trung tâm giao dịch (Trading Center)

- Đã sửa lại file demo notebook để cập nhật các hàm mới.
- Khôi phục giá đơn vị của stock_historical_data từ 1000 VND thành VND bằng cách nhân với 1000.
- Hàm **price_board** đã được cập nhật.
- Bổ sung hàm mới trong mô đun **utils.py** để trích xuất giá trị ngày tháng theo định dạng YYYY-mm-dd.

### 05-07-2023
- Cập nhật file README.md (áp dụng cho tiếng Việt trước).
- Các hàm liên quan đến nguồn dữ liệu SSI không hoạt động đã bị loại bỏ.
- Hàm **financial_ratio** đã được cải tiến với các cập nhật sau đây:
  - DataFrame kết quả bây giờ có cấu trúc được chuyển vị (transpose), với năm/quý đóng vai trò là chỉ mục, giúp sử dụng thuận tiện hơn.
  - Tham số **is_all** đã trở thành tham số phụ tùy chọn.
- Hàm **industry_analysis** và stock_ls_analysis đã được cải thiện:
  - DataFrame kết quả bây giờ có cấu trúc được chuyển vị, với tên mã cổ phiếu làm tiêu đề cột, giúp dễ sử dụng.
  - Thêm tham số **lang**, cho phép hiển thị cột DataFrame bằng nhãn tiếng Việt hoặc tiếng Anh.

### 29-06-2023
- Đã cập nhật hàm stock_intraday_data để cung cấp thêm dữ liệu chi tiết trả về bởi hàm và dễ sử dụng hơn
- Cập nhật hàm stock_historical_data để hỗ trợ lấy dữ liệu lịch sử về các chỉ số.

### 22-06-2023
- Phát hành phiên bản 0.15 rên Pypi.
- Giới thiệu một tính năng mới cho hàm stock_historical_data, cho phép lấy dữ liệu với nhiều độ phân giải thời gian khác nhau. Đã nâng cấp API tương ứng hỗ trợ hàm này.
  - Bao gồm tham số độ phân giải để cho phép người dùng lấy dữ liệu giá tại các khoảng thời gian 1 phút, 3 phút, 5 phút, 15 phút, 30 phút, 1 giờ hoặc 1 ngày.
  - Sửa tên cột trong bảng dữ liệu trả về từ tradingDate thành time.
- Đã đánh dấu rõ các hàm không khả dụng cho các API liên quan tới SSI.
- Tùy chọn **mode='live'** trong hàm listing_companies() đã được loại bỏ. Hàm này bây giờ chỉ đọc danh sách công ty từ tệp csv trên repo github này.
- Cập nhật cây thư mục cho github repo, thêm thư mục dữ liệu và thêm tệp dữ liệu, thư mục demo để lưu trữ các tệp demo.

### 07-06-2023
Chính thức hỗ trợ hướng dẫn sử dụng bằng tiếng Việt cho tệp thư viện thông qua file README.md, giúp thúc đẩy khả năng tiếp cận với vnstock cho người dùng Việt Nam.

### 20-05-2023
- Nhánh **main** dành riêng cho các cập nhật quan trọng, trong khi nhánh **beta** được sử dụng cho các cập nhật nhỏ. Từ bây giờ, gói PyPI sẽ phản ánh nội dung của nhánh **main**.
- Hàm listing_companies() bây giờ có thể đọc danh sách công ty từ tệp csv trên repo github này hoặc từ một yêu cầu API trực tiếp.
- Hàm stock_intraday_data() bây giờ có một giới hạn mới là 100 cho tham số page_size do TCBS thiết lập.