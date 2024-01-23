# Lịch sử cập nhật
## 23-1-2024

!!! hot "Cập nhật bản 2.8.8"
	Cập nhật thay đổi từ ngày 16/12/2023 ở phiên bản `beta` sang `main` và phát hành chính thức phiên bản 2.8.8. 
	
- Cập nhật mã nguồn hàm `financial_report` sửa lỗi triệt để lỗi sử dụng 'Excel file format cannot be determined, you must specify an engine manually' do dữ liệu trả về không phải định dạng Excel.
  -   Nguồn dữ liệu từ Fiintrade của SSI sử dụng mã `OrganCode` để tra cứu thông tin công ty trong đó có báo cáo tài chính. Có khoảng > 600 mã cổ phiếu có mã symbol khác OrganCode do đó có nhiều mã khi tra cứu BCTC với mã symbol sẽ gây ra rỗi trong khi với các mã khác thì không. Ví dụ `YTC` có OrganCode là `YTECO` dùng để tra cứu BCTC.
  -   Bổ sung `openpyxl` là gói phụ thuộc để đọc dữ liệu trả về từ API dưới dạng file Excel. Lỗi này xảy ra khi cài bản Python thuần. Không gặp lỗi với Google Colab hoặc Anaconda.

## 21-1-2024
- Bổ sung tích hợp cho phép sử dụng các hàm gửi tin nhắn từ vnstock qua Telegram/Slack với các channel/group chat được cài đặt.
- Cập nhật nội dung trang tài liệu
- Khởi động dự án vnstock-next cho thế hệ phần mềm vnstock tiếp theo.

## 3-1-2024

- Cập nhật khung chương trình khóa học Python 5 khai giảng 21/1/2024

- Bổ sung tính năng hiện banner thông báo quan trọng trên trang tài liệu.

## 2-1-2024

- Bổ sung tính năng OCR sử dụng Pytesseract cho vnstock và vnstock-data-pro. Chi tiết [tại đây](https://docs.vnstock.site/integrate/pytesseract-ocr-chuyen-doi-tai-lieu-tai-chinh-scan-sang-van-ban/)
  
## 24-12-2023
- Cập nhật tài liệu dự án
  - Tài liệu truy xuất [giá lịch sử](https://docs.vnstock.site/functions/technical/)
  - Hướng dẫn [truy xuất dữ liệu giao dịch nước ngoài/tự doanh](https://docs.vnstock.site/functions/market/#giao-dich-ntnn) sử dụng gói phần mềm `vnstock-data-pro`
  - Hướng dẫn nhanh

## 16-12-2023

- Cập nhật tài liệu dự án
  
  - Bổ sung hướng dẫn sử dụng tích hợp SSI Fast Connect API trong gói `vnstock-pro-data` [tại đây](https://docs.vnstock.site/integrate/ssi_fast_connect_api/)
  - Bổ sung thông tin chi tiết chương trình Vnstock Insider Program [tại đây](https://docs.vnstock.site/insiders-program/gioi-thieu-chuong-trinh-vnstock-insiders-program)

- Bổ sung `requirements.txt` cho trình tạo trang tĩnh MKDocs giúp cài đặt gói phụ thuộc để thiết lập trang tài liệu và xem trước dễ dàng.
  
## 14-12-2023
  
  Chính thức phát hành các thay đổi từ nhánh Beta trong phiên bản 2.8.7. Chi tiết cập nhật qua blog: [tại đây](https://vnstock.site/2023/12/15/ra-mat-vnstock-insider-program-cap-nhat-nhieu-tinh-nang-thu-vi/)

- Ra mắt Vnstock Insiders Program cung cấp quyền truy cập tới các kho chứa mã nguồn riêng tư (private repo)

- Ra mắt `vnstock-pro-data` trong chương trình Insiders, cung cấp khả năng truy cập dữ liệu chất lượng cao với độ trễ thấp.
  
  - Tải dữ liệu giá OHLCV nhanh chóng, chính xác không cần xác thực qua Public API của SSI.
  - Tải và streaming dữ liệu qua SSI Fast Connect API chính thức (cần đăng ký và xác thực người dùng)

- Chính thức phát hành tính năng truy cập dữ liệu quỹ mở. Hướng dẫn [tại đây](https://docs.vnstock.site/functions/funds/)

- Hỗ trợ xuất dữ liệu time series cho OpenBB Terminal. Hướng dẫn [tại đây](https://docs.vnstock.site/integrate/OpenBBTerminal/)

- Cập nhật tài liệu dự án

## 10-12-2023

- Bổ sung tính năng truy xuất dữ liệu quỹ mở từ fmarket.vn, phát triển từ mã nguồn do `andrey_jef` đóng góp. Tài liệu mô tả và demo notebook đã được cập nhật tương ứng.
- Đưa `plotly` thành thư viện tùy chọn, chỉ phải import vào dự án nếu người dùng có nhu cầu sử dụng tính năng vẽ đồ thị. Việc này giúp vnstock chạy trên môi trường khác Google Colab không cần cài đặt thêm `plotly` theo mặc định. Mã nguồn được cập nhật lên bản beta trên Github, thay đổi sẽ được đẩy lên PyPI trong tuần tới.
- Cập nhật tài liệu hướng dẫn cho nội dung lấy dữ liệu giá lịch sử.
- Cập nhật tài liệu hướng dẫn cách cài đặt thư viện TA-Lib cho phân tích kỹ thuật trên máy tính Windows.

## 09-11-2023

> Phát hành phiên bản 0.2.8.5

- Cập nhật hàm `stock_intraday_data`
  - Bổ sung tham số `investor_segment`, mặc định nhận giá trị `True` cho phép trả về dữ liệu khớp lệnh theo phân nhóm nhà đầu tư (như các phiên bản trước), khi đặt là `False` cho phép trả về dữ liệu thô, không gộp thông tin lệnh theo phân nhóm.
- Bổ sung hàm `amibroker_ohlc_export` cho phép xuất dữ liệu sang định dạng CSV để nạp dữ liệu cho Amibroker. Chi tiết [tại đây](http://docs.vnstock.site/integrate/amibroker/)
- Bổ sung hướng dẫn tích hợp vnstock với dự án sử dụng thư viện phân tích kỹ thuật TA-lib python. Chi tiết [tại đây](http://docs.vnstock.site/integrate/ta_lib/)
- Giới thiệu một số thư viện Backtesting trong python giúp kiểm thử chiến lược giao dịch. Chi tiết [tại đây](http://docs.vnstock.site/integrate/backtesting/)

## 08-11-2023

> Phát hành phiên bản 0.2.8.4

- Tùy biến hàm `stock_historical_data` giúp dễ dàng sử dụng với các thư viện phân tích kỹ thuật khác trong Python.
  
  - Thêm tham số `decor`, nhận giá trị mặc định là `False` (không thay đổi dữ liệu trả về với cách sử dụng hiện tại của người dùng). Khi đặt `decor=True`, áp dụng thay tên các cột trong DataFrame trả về dưới dạng Title Case tức `Open, High, Low, Close, Time, Ticker` thay vì `open, high, low, close, time, ticker` như hiện tại đồng thời đặt cột Time là index. Việc này giảm bớt cho người dùng phải viết thêm câu lệnh khi sử dụng dữ liệu vnstock kết hợp các thư viện phân tích kỹ thuật phổ biến vốn dùng thư viện Yahoo Finance làm nguồn cấp dữ liệu.
  
  - Bổ sung tham số `source` cho phép chọn nguồn tải dữ liệu là `TCBS` hay `DNSE`. Nguồn dữ liệu `TCBS` cho lấy dữ liệu lịch sử theo ngày (resolution = `1D`) trong thời gian dài, không hỗ trợ khung thời gian nhỏ hơn. Trong khi đó nguồn dữ liệu `DNSE` cho phép lấy dữ liệu với nhiều khung thời gian khác nhau, giới hạn 90 ngày gần nhất đối với dữ liệu phút, 10 năm gần nhất đối với dữ liệu ngày.

- Cập nhật tcbs_headers sử dụng cho các request đến API của TCBS

## 05-11-2023

- Hoàn thiện tích hợp đầy đủ DNSE Lightspeed API vào mã nguồn vnstock. Phát hành phiên bản 0.2.8.2. Sử dụng lệnh `pip install -U vnstock` để cập nhật phiên bản.

## 29-10-2023

- Tích hợp API endpoints cơ bản của DNSE vào vnstock
  - Demo cho các nhà đầu tư cách tạo 1 request và kết nối hệ thống DNSE để lấy JWT token
  - Demo xuất thông tin tài khoản
- Cập nhật tài liệu sử dụng

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

## 22-07-2023

- Bổ sung hướng dẫn vào [Demo Notebook](https://github.com/thinh-vu/vnstock/blob/beta/demo/gen2_vnstock_demo_index_all_functions_testing_2023.ipynb) giúp người dùng xuất dữ liệu từ Google Colab ra Google Sheets.

## 14-07-2023

- Phát hành phiên bản 0.17 trên PyPI.
- Những thay đổi trên nhánh **beta** sẽ được cập nhật vào nhánh **main** và phát hành qua PyPI hàng tháng từ bây giờ.
- File README.md đã được cập nhật để đồng bộ hóa phiên bản tiếng Anh và tiếng Việt.
- Dữ liệu file listing_companies_enhanced-2023.csv trong thư mục data của repo này được sử dụng để cung cấp dữ liệu công ty niêm yết cho hàm listing_companies.
- Hàm mới, price_depth, đã được giới thiệu để lấy giá và khối lượng giao dịch cho danh sách các cổ phiếu. Hàm này có thể được sử dụng song song với hàm price_board.

## 13-07-2023

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

## 05-07-2023

- Cập nhật file README.md (áp dụng cho tiếng Việt trước).
- Các hàm liên quan đến nguồn dữ liệu SSI không hoạt động đã bị loại bỏ.
- Hàm **financial_ratio** đã được cải tiến với các cập nhật sau đây:
  - DataFrame kết quả bây giờ có cấu trúc được chuyển vị (transpose), với năm/quý đóng vai trò là chỉ mục, giúp sử dụng thuận tiện hơn.
  - Tham số **is_all** đã trở thành tham số phụ tùy chọn.
- Hàm **industry_analysis** và stock_ls_analysis đã được cải thiện:
  - DataFrame kết quả bây giờ có cấu trúc được chuyển vị, với tên mã cổ phiếu làm tiêu đề cột, giúp dễ sử dụng.
  - Thêm tham số **lang**, cho phép hiển thị cột DataFrame bằng nhãn tiếng Việt hoặc tiếng Anh.

## 29-06-2023

- Đã cập nhật hàm stock_intraday_data để cung cấp thêm dữ liệu chi tiết trả về bởi hàm và dễ sử dụng hơn
- Cập nhật hàm stock_historical_data để hỗ trợ lấy dữ liệu lịch sử về các chỉ số.

## 22-06-2023

- Phát hành phiên bản 0.15 rên Pypi.
- Giới thiệu một tính năng mới cho hàm stock_historical_data, cho phép lấy dữ liệu với nhiều độ phân giải thời gian khác nhau. Đã nâng cấp API tương ứng hỗ trợ hàm này.
  - Bao gồm tham số độ phân giải để cho phép người dùng lấy dữ liệu giá tại các khoảng thời gian 1 phút, 3 phút, 5 phút, 15 phút, 30 phút, 1 giờ hoặc 1 ngày.
  - Sửa tên cột trong bảng dữ liệu trả về từ tradingDate thành time.
- Đã đánh dấu rõ các hàm không khả dụng cho các API liên quan tới SSI.
- Tùy chọn **mode='live'** trong hàm listing_companies() đã được loại bỏ. Hàm này bây giờ chỉ đọc danh sách công ty từ tệp csv trên repo github này.
- Cập nhật cây thư mục cho github repo, thêm thư mục dữ liệu và thêm tệp dữ liệu, thư mục demo để lưu trữ các tệp demo.

## 07-06-2023

Chính thức hỗ trợ hướng dẫn sử dụng bằng tiếng Việt cho tệp thư viện thông qua file README.md, giúp thúc đẩy khả năng tiếp cận với vnstock cho người dùng Việt Nam.

## 20-05-2023

- Nhánh **main** dành riêng cho các cập nhật quan trọng, trong khi nhánh **beta** được sử dụng cho các cập nhật nhỏ. Từ bây giờ, gói PyPI sẽ phản ánh nội dung của nhánh **main**.
- Hàm listing_companies() bây giờ có thể đọc danh sách công ty từ tệp csv trên repo github này hoặc từ một yêu cầu API trực tiếp.
- Hàm stock_intraday_data() bây giờ có một giới hạn mới là 100 cho tham số page_size do TCBS thiết lập.