# SSI Fast Connect API

!!! abstract "Fast Connect API"
    SSI cung cấp bộ APIs cho phép thiết lập giao dịch tự động (FastConnect Trading) và truy xuất dữ liệu thị trường chứng khoán cơ bản (FastConnect Data) cho ngôn ngữ Python. Công cụ này hoàn toàn miễn phí, bạn có thể xin cấp quyền sử dụng bằng cách mang CCCD ra phòng giao dịch của SSI gần nhất để đăng ký và kích hoạt. 
    
vnstock cung cấp tới các bạn các hàm được tùy biến sẵn giúp dễ dàng sử dụng mà không cần bỏ nhiều thời gian nghiên cứu và tùy biến từ demo sơ khai do SSI cung cấp. Bạn có thể sở hữu gói phần mềm tích hợp này thông qua chương trình Github Sponsor. Theo đó, bạn sẽ trở thành nhà tài trợ của vnstock để có thể truy cập và sử dụng các tính năng này được phát hành dưới dạng gói phần mềm nâng cao cho vnstock. Truy cập [trang tài trợ](https://github.com/sponsors/thinh-vu) và chọn gói phù hợp và thanh toán bằng thẻ Visa/Master để có thể sử dụng ngay hôm nay.

[Kết nối SSI với vnstock :material-rocket-launch:](https://github.com/sponsors/thinh-vu){ .md-button }

**Chia sẻ thêm:**

Để có thể sử dụng thành thạo `ssi_fc_data` và `ssi_fc_trading`, bạn cần có kiến thức Python vững và dành nhiều thời gian nghiên cứu bởi những đoạn code mẫu được cung cấp ở mức tối thiểu để demo tính năng. Dữ liệu chỉ được in ra màn hình mà không phải được trả về dưới dạng các Python object để sử dụng dễ dàng. Vấn đề này tôi đã gửi [ticket](https://github.com/SSI-Securities-Corporation/python-fcdata/issues/1) và yêu cầu giải đáp từ team Dev của SSI, bạn có thể theo xem chi tiết tại link. Team dev SSI thường không phản hồi bạn qua Github nhanh chóng. Tài liệu của SSI cũng đã được cập nhật chuẩn hơn sau lần cập nhật gần đây sau khi nhận được đóng góp ý kiến.

- Tài liệu sử dụng chính thức từ SSI: [Tại đây](https://guide.ssi.com.vn/ssi-products/v/tieng-viet/fastconnect-data/du-lieu-streaming)

## vnstock x SSI Fast Connect API?

- Sử dụng FastConnect Data API bạn có thể nhận dữ liệu giá cổ phiếu đang được giao dịch theo thời gian thực với 10 bước giá và khối lượng. Đây là một tài nguyên quý giá cho các nhà đầu tư để nắm bắt thông tin thị trường nhanh chóng và ra quyết định thông minh.

- Sử dụng FastConnect Trading API bạn có thể đặt lệnh mua/bán cổ phiếu theo thời gian thực. Đây là một công cụ hữu ích để xây dựng các bot giao dịch tự động.

- vnstock phát triển cho ngôn ngữ Python, bạn có thể tích hợp với bất cứ thư viện nào trong môi trường Python. vnstock hoạt động hoàn hảo và nhanh chóng.

- vnstock giúp bổ sung khuyết điểm của hai APIs trên ở những nhóm tính năng sau:
    - vnstock cung cấp dữ liệu phân tích cơ bản hoàn chỉnh, trong khi SSI chỉ cung cấp dữ liệu giao dịch.
    - Các hàm vnstock được phát triển thân thiện với người dùng, ít mất thời gian làm quen, dữ liệu trả về dữ liệu là DataFrame dễ dàng thao tác và phân tích thay vì chỉ in thông tin ra Terminal như ví dụ minh họa từ SSI và không kèm tài liệu hướng dẫn tùy biến nâng cao.
    - vnstock tự hào là gói phần mềm mã nguồn mở được cung cấp tài liệu sử dụng một cách bài bản, khoa học cùng sự hỗ trợ tuyệt vời từ tác giả. Một phần mềm hoàn hảo chỉ khi đi kèm với hướng dẫn sử dụng để ngay cả những người không có kiến thức kỹ thuật cũng có thể thấy giá trị ngay lập tức qua vài thao tác.

- Bạn có thể sử dụng vnstock trong việc xây dựng trung tâm phân tích dữ liệu của riêng mình giúp đưa ra các quyết định đầu tư một cách nhanh chóng, đầy đủ thông tin. Kết hợp vưới việc sử dụng API từ SSI, đảm bảo bạn đã có trọn bộ công cụ giao dịch nhanh chóng, toàn vẹn. Xem thêm video dưới đây để hiểu rõ hơn về cách sử dụng.

<iframe width="1024" height="600" src="https://www.youtube.com/embed/mOT7IczFJMo?si=pSo5SUEInzWR0Vam" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>



