
<div id="logo" align="center">
    <img src="https://thinh-vu.github.io/FinancialModelingPrep/assets/fmp_logo.png" alt= "logo"/>
    <img src = "https://thinh-vu.github.io/FinancialModelingPrep/assets/vnstock_logo_color.png" alt="vnstock_logo"/>
</div>
## Giới thiệu

13/10/2023, Vnstock chính thức giới thiệu thư viện Python giúp tích hợp hoàn hảo API dữ liệu chứng khoán, tài chính toàn cầu từ nhà từ FinancialModelingPrep (FMP) vào các dự án khoa học dữ liệu và đầu tư thực tế.

!!! info "Giới thiệu"
	[FinancialModelingPrep API](https://intelligence.financialmodelingprep.com/pricing-plans?couponCode=thinhvu&utm_source=github&utm_medium=thinhvu_repos&utm_campaign=thinhvu) cung cấp một nền tảng dữ liệu tài chính toàn diện cho phép truy cứu dữ liệu lịch sử tới 30 năm với độ phủ trên 40.000 mã cổ phiếu, tiền mã hóa, ngoại hối, hàng hóa trên toàn thế giới. API này cung cấp dữ liệu từ trên 90 sàn giao dịch tại 46 quốc gia trên thế giới. Dữ liệu có độ phủ toàn bộ sàn giao dịch ở Hoa Kỳ cho tới XETRA, EURONEX, TSX, SEDAR, SEHK và hơn thế. Vnstock sẽ tích hợp trực tiếp thư viện FMP vào mã nguồn trong các bản phát hành tiếp theo.

[Tìm hiểu thêm :material-arrow-right:](https://intelligence.financialmodelingprep.com/pricing-plans?couponCode=thinhvu&utm_source=github&utm_medium=thinhvu_repos&utm_campaign=thinhvu){ .md-button }

## Thư viện FinancialModelingPrep Python có gì?

Với FinancialModelingPrep Python, bạn sẽ có thể truy cập hầu hết các loại dữ liệu quan trọng mà FinancialModelingPrep API cung cấp trong môi trường Python một cách dễ dàng. Dưới đây là danh mục các dữ liệu đang được hỗ trợ:

- **Dữ Liệu Cơ Bản:**
    - **Danh Sách Cổ Phiếu**: Lấy thông tin danh sách toàn bộ cổ phiếu được cung cấp.
    - **Thông Tin Công Ty**: Khám phá thông tin chi tiết về các công ty, dữ liệu tài chính và các chỉ số quan trọng.
    - **Phân Tích Báo Cáo**: Truy cập các báo cáo tài chính, bao gồm báo cáo kinh doanh, báo cáo cân đối kế toán và báo cáo lưu chuyển tiền tệ.
    - **Lịch Giao Dịch Cổ Phiếu**: Cập nhật thông tin về các sự kiện quan trọng như kết quả tài chính, cổ tức, chia cổ tức và IPO.
    - **Tin Tức**: Tiếp cận nhiều loại tin tức khác nhau, bao gồm tin tức tổng hợp, tin tức cổ phiếu, tin tức tiền mã hóa (crypto), tin tức các cặp ngoại hối (forex) và thông cáo báo chí.
    - **Giao Dịch Nội Bộ**: Theo dõi các hoạt động giao dịch nội bộ.  
        **Dữ Liệu Thị Trường:**
    - **Tổng Quan Thị Trường**: Thông tin tổng quan về điều kiện thị trường.
    - **Dữ Liệu Kinh Tế**: Truy cập các chỉ số kinh tế và dữ liệu có thể ảnh hưởng đến chiến lược tài chính của bạn.
    - **Cổ Phiếu, Tiền Điện Tử (Crypto), Ngoại Hối (Forex) và Hàng Hóa (Commodities)**: Cập nhật về xu hướng, giá cả và dữ liệu lịch sử cho nhiều loại tài sản khác nhau.
	- **Dữ Liệu Báo Giá:** Nhận dữ liệu báo giá thời gian thực và lịch sử cho cổ phiếu, tiền điện tử, ngoại hối và hàng hóa. Dữ liệu được cung cấp với độ chi tiết từ 1 phút, 15 phút, 30 phút, 1 giờ và ngày giúp bạn theo dõi sát sao diễn biến thị trường theo thời gian thực.
## Sử dụng như thế nào

- **Cài đặt thư viện** dễ dàng bằng công cụ pip với dòng lệnh:  
`pip install --upgrade FinancialModelingPrep-Python`
- **Bạn cần đăng ký một tài khoản FinancialModelingPrep** để sử dụng, có thể đăng nhập nhanh bằng tài khoản Google sẵn có và chọn gói dịch vụ phù hợp sau đó tạo API key và sử dụng. Bạn có thể chọn gói BASIC hoàn toàn miễn phí để bắt đầu. Với lựa chọn này, bạn truy cập được dữ liệu cuối ngày của các giao dịch, giới hạn dữ liệu trong vòng 5 năm tuy nhiên vẫn sử dụng được nhiều loại dữ liệu dễ dàng. Nếu gói dịch vụ BASIC chưa đáp ứng nhu cầu, bạn hãy cân nhắc lựa chọn nâng cấp lên gói dịch vụ phù hợp, các mức giá hiện tại của FinancialModelingPrep rất phải chăng.
- **Khi sử dụng [liên kết](https://intelligence.financialmodelingprep.com/pricing-plans?couponCode=thinhvu&utm_source=github&utm_medium=thinhvu_repos&utm_campaign=thinhvu) trong tài liệu hướng dẫn để nâng cấp tài khoản, bạn được tự động áp dụng mức chiết khấu 20%.**
- Để thử nghiệm nhanh chóng và thấy ngay kết quả trả về từ các hàm, bạn có thể sử dụng Demo Notebook được cấu trúc chặt chẽ và cung cấp sẵn các hàm có trong thư viện.

[Tài liệu chính thức :material-arrow-right:](https://thinh-vu.github.io/FinancialModelingPrep?utm_source=vnstock.site&utm_medium=blog&utm_content=release_announcement){ .md-button }