# Đóng góp mã nguồn

!!! abstract "Lời nói đầu"
    Cám ơn bạn đã quan tâm đến việc đóng góp mã nguồn cho dự án Vnstock. Bạn có thể chọn nhiều hình thức đóng góp khác nhau, trong đó bao gồm nhưng không giới hạn các việc như xây dựng và cải tiến mã nguồn hoặc dịch tài liệu của dự án.

## Triết lý thiết kế

Hầu hết mã nguồn Vnstock cho đến thời điểm 11/2023 đều do một mình tác giả phát triển và thực sự đây là một nỗ lực rất lớn với khối lượng công việc khổng lồ. Nhằm tối ưu hóa nguồn lực và tập trung vào những điều có giá trị, những ưu tiên và triết lý thiết kế Vnstock được tôi sử dụng như sau:

1. **DỄ DÀNG, THUẬN TIỆN:** Vnstock được thiết kế phục vụ đối tượng người dùng đa dạng, giúp phổ biến công cụ này tới cả những người không có kiến thức lập trình từ trước. Nguyên tắc ngày giúp ai cũng đều có thể nhanh chóng sử dụng Vnstock (tương tự như gọi các hàm Excel, chỉ khác chút là trong môi trường Python).
2. **THẤU HIỂU NGƯỜI DÙNG** (end-user): Để làm rõ hơn ý 1 ở trên, các tính năng mà Vnstock cung cấp hướng đến đối tượng người dùng cuối (ít hoặc chưa có kiến thức lập trình), do đó trong quá trình phát triển tính năng, tôi cố gắng đặt mình vào vị trí và góc nhìn của người dùng cuối để tạo ra những trải nghiệm sử dụng thân thiện và dễ dàng. Nếu bạn đóng góp mã nguồn để giúp chính mình sử dụng thuận tiện cho công việc cũng không sao. Tôi sẽ cùng bạn tối ưu thêm các bước cần thiết để chúng thân thiện hơn với số đông người dùng.
3. **TÍNH NĂNG ĐA DẠNG**: Tôi ưu tiên tăng độ phủ các tính năng và nguồn cấp dữ liệu để giúp Vnstock đáp ứng nhu cầu đa dạng của người dùng trong khi nguồn lực phát triển hạn chế. Do đó, các tính năng có thể chưa hoàn toàn tối ưu, và sẽ được cải tiến thêm qua thời gian để tối ưu hiệu suất sử dụng. 
4. **"SURVIVE, THEN THRIVE"**: Các nguồn cấp dữ liệu hiện tại của Vnstock có được thông qua thủ thuật Web Scraping, việc này không đảm bảo việc tồn tại lâu dài của nguồn cấp dữ liệu bởi nhà cung cấp có thể ngăn chặn hoặc từ chối hoàn toàn truy cập của bạn. Do đó, hãy  đảm bảo rằng tính năng được xây dựng có thể sống sót an toàn trước khi bỏ quá nhiều công sức vào việc tối ưu tận gốc nhưng bỗng dưng một ngày bạn nhận ra mình là "Dã tràng xe cát biển Đông" khi tính năng mình xây dựng bị ngưng hoạt động.

## Hướng phát triển Vnstock

> Bạn có thể đóng góp tính năng mình cảm thấy cần thiết hoặc phù hợp với những gì vnstock hiện có. Vnstock không chỉ dừng lại ở một gói phần mềm truy xuất dữ liệu hay chỉ giới hạn với chứng khoán Việt Nam mà mục tiêu lớn nhất là phục vụ người Việt, và do người Việt phát triển. 

Dưới đây là các nhóm thông tin/tính năng bạn có thể tham khảo để phát triển.

### Truy xuất dữ liệu
- Dữ liệu kinh tế vĩ mô
- Tin tức báo chí, sự kiện: giúp các bạn làm nghiên cứu theo hướng định lượng tiếp cận dữ liệu dễ dàng hơn.
- Dữ liệu giao dịch quỹ, tiền tệ, hàng hóa, crypto, chứng quyền, vv
### Tính toán
- Tính toán các chỉ báo kỹ thuật, mô hình nến, điểm mua/bán, vv dựa trên tiêu chuẩn dữ liệu Vnstock đang cung cấp
- Xử lý ngôn ngữ tự nhiên, phân loại sự kiện, vv
### Biểu diễn dữ liệu
- Cung cấp các phương thức giúp trực quan hóa dữ liệu và tìm cơ hội đầu tư/nghiên cứu nhanh chóng. Trước tiên, đưa các trải nghiệm và tính năng quen thuộc với số đông từ các phần mềm phân tích khác sang Vnstock để thúc đẩy việc phổ biến Vnstock tới cộng đồng.
- Cung cấp các data app mẫu, ví dụ Streamlit để khuyến khích cộng đồng phát triển thêm tính năng và sử dụng.
### Tích hợp
- Tích hợp với các thư viện uy tín, sẵn có trong hệ sinh thái Python
- Tích hợp tính năng liên kết với các đối tác cung cấp dịch vụ, ví dụ SSI và fc_data
### AI & ML
- Sử dụng Vnstock trong các dự án về máy học và AI trong thực tế đồng thời tạo ra các tính năng giúp việc triển khai Vnstock vào nhóm công việc này dễ dàng hơn.
### Tự động hóa và bot
- Xây dựng các tính năng giúp triển khai Vnstock dưới dạng Bot hoặc dự án tự động phục vụ cho việc cảnh báo/hoặc tham gia một phần trong việc xây dựng chương trình giao dịch tự động.
### Hướng dẫn (demo & tutorial)
- Cung cấp các ví dụ sinh động và cách sử dụng Vnstock hiệu quả trong thực tế giúp cộng đồng học hỏi và tiếp cận các phương pháp tiên tiến.

## Khởi động

> Tôi tin là tới đây, bạn đã có đủ thông tin để bắt đầu hành trình code dạo cùng Vnstock. Dưới đây là những hướng dẫn giúp bạn bắt đầu dễ dàng hơn.

1. **Folk** nhánh **beta** của repo này về tài khoản của mình, sửa đổi mã nguồn và tạo **pull request** để yêu cầu cập nhật mã nguồn. Sau khi kiểm tra các thay đổi và phê duyệt, mã nguồn do bạn đóng góp sẽ được gộp vào vnstock.
2. Tạo **Pull Request** (PR) để gửi những thay đổi về mã nguồn của bạn tới nhánh `beta` để yêu cầu duyệt và cập nhật mã nguồn khi công việc hoàn thành. Những thay đổi do bạn đóng góp sẽ được cập nhật trên nhánh `beta` để thử nghiệm, sau đó phát hành chính thức trong phiên bản tiếp theo của **vnstock** trên Pypi.org cùng những cập nhật của tác giả.

## Kênh thông tin trao đổi

> Các trao đổi với tác giả trong việc lập trình và đóng góp mã nguồn cho dự án Vnstock, bạn vui lòng sử dụng một trong các tùy chọn sau.

1. Kênh [🧰nhóm-phát-triển](https://discord.com/channels/1096588264254738482/1133760970850832414) trên Discord. Nếu bạn chưa tham gia Discord của Vnstock, hãy tham gia [tại đây](https://discord.gg/6uMq5wZhY4). Trao đổi qua tin nhắn giúp thúc đẩy nhanh quá trình triển khai và xử lý các vấn đề phát sinh nhanh chóng.
2. Mục [Discussion](https://github.com/thinh-vu/vnstock/discussions) có sẵn trên trang Github của dự án. Bạn có thể tạo chủ đề mới hoặc tham gia các chủ đề đã có để trao đổi các ý kiến của mình.

## Tinh thần hợp tác

Tôi hướng đến một môi trường trao đổi thân thiện, tích cực và thúc đẩy hợp tác khi mời các bạn tham gia xây dựng vnstock. Để mọi thứ rõ ràng và minh bạch, tôi chia sẻ tới các bạn những nguyên tắc giúp chúng ta hợp tác dễ dàng hơn trong khuôn khổ một dự án mã nguồn mở như sau:

1. **Hạn chế cảm cảm tính khi trao đổi công việc**: Điều này có được dựa trên việc chúng ta hiểu về những nguyên tắc và nhu cầu của nhau để cả đôi bên ít phải đi lòng vòng trao đổi một cách mơ hồ.
2. **Lắng nghe và tôn trọng ý kiến của nhau**: Việc các bạn đóng góp mã nguồn không giống như cơ chế xin - cho mà là cả tôi, bạn và cộng đồng cùng hưởng lợi. Những ý kiến của bạn luôn được tôn trọng, và tác giả cũng cố gắng trao đổi với tư duy cởi mở, hướng đến kết quả tốt nhất có thể cho dự án.

## Tiêu chuẩn đóng góp

### Quy tắc đặt tên và mô tả
- Đặt tên nhánh: **feat/tieu-de-tinh-nang** hoặc **fix/tieu-de-sua-loi**.
- Mô tả Pull Request: Mô tả rõ ràng và ngắn gọn về tính năng mới hoặc lý do sửa lỗi.

### Quy tắc mã nguồn
- Tham khảo [PEP8](https://www.python.org/dev/peps/pep-0008/) cho Python để tạo ra mã nguồn sạch sẽ, mạch lạc, và thuận tiện nhất trong việc hợp tác phát triển.
- Đảm bảo rằng mã nguồn của bạn đã được kiểm thử kỹ hạn chế không gây ra lỗi khác trong dự án.
- Để lại comment cho các đoạn mã bạn cung cấp giúp các thành viên khác hiểu được logic thiết kế và bắt kịp ý tưởng của bạn tốt hơn.

## Bản quyền và giấy phép
- Bằng cách đóng góp vào dự án Vnstock, bạn đồng ý rằng đóng góp của bạn sẽ được công bố tự do theo giấy phép [MIT License](https://github.com/thinh-vu/vnstock/blob/legacy/LICENSE).
- Vui lòng thêm tên của bạn vào phần "Người đóng góp" trong tệp [CONTRIBUTORS.md](https://github.com/thinh-vu/vnstock/blob/legacy/CONTRIBUTORS.md).

Chúng tôi cảm ơn sự đóng góp của bạn cho Vnstock. Nhóm phát triển sẵn lòng hỗ trợ và xem xét mọi đóng góp để nâng cao chất lượng và tính năng của dự án. Hãy cùng nhau tạo nên một công cụ mạnh mẽ hỗ trợ đầu tư chứng khoán Việt Nam! 🚀