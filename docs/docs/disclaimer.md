# Miễn trừ trách nhiệm

## Đối với người dùng

!!! tip "Quan điểm phát triển sản phẩm"
    vnstock được phát triển nhằm mục đích cung cấp các công cụ nghiên cứu đơn giản và miễn phí, nhằm giúp người nghiên cứu tiếp cận và phân tích dữ liệu chứng khoán một cách dễ dàng. Dữ liệu được cung cấp phụ thuộc vào nguồn cấp dữ liệu, do đó, khi sử dụng, bạn cần thận trọng và cân nhắc.

💰 Trong bất kỳ trường hợp nào, người sử dụng hoàn toàn chịu trách nhiệm về quyết định sử dụng dữ liệu trích xuất từ vnstock và chịu trách nhiệm với bất kỳ tổn thất nào có thể phát sinh. Bạn nên tự mình đảm bảo tính chính xác và đáng tin cậy của dữ liệu trước khi sử dụng chúng. Mã nguồn mở của dự án cho phép bạn xác thực thông tin và quá trình biến đổi để trả về dữ liệu cuối cùng.

Việc sử dụng dữ liệu chứng khoán và quyết định đầu tư là hoạt động có rủi ro và có thể gây mất mát tài sản. Bạn nên tìm kiếm lời khuyên từ các chuyên gia tài chính và tuân thủ các quy định pháp luật về chứng khoán tại Việt Nam và quốc tế khi tham gia vào hoạt động giao dịch chứng khoán.

Xin lưu ý rằng vnstock không chịu trách nhiệm và không có bất kỳ trách nhiệm pháp lý nào đối với bất kỳ tổn thất hoặc thiệt hại nào phát sinh từ việc sử dụng gói phần mềm này.

Việc truy xuất dữ liệu hàng loạt thông qua các vòng lặp hoặc chương trình gửi yêu cầu (request) hàng loạt trong thời gian ngắn đến cơ sở dữ liệu cùa nguồn cấp dữ liệu không được khuyến khích. Người dùng cần ý thức được hành động của mình để tránh gây tổn thất đến hệ thống của nguồn cấp dữ liệu và liên quan đến các rủi ro pháp lý liên quan, bởi ranh giới của việc truy cập dữ liệu và tạo ra một cuộc tấn công từ chối truy cập tới máy chủ của nguồn cấp dữ liệu là tương đối mong manh.

## Đối với công ty chứng khoán, nguồn cấp dữ liệu

!!! tip "Quan điểm thiết kế"
    🐱‍👤 vnstock được thiết kế hoàn toàn cho mục đích phân tích và thực hành nghiên cứu đầu tư. Mọi hình thức sử dụng không đúng mục đích hoặc việc sử dụng trái phép thư viện với mục đích xấu như tấn công public API hay gây hại cho hệ thống thông qua từ chối truy cập hoặc các hành động tương tự, hoàn toàn nằm ngoài phạm vi sử dụng dự định và không thuộc trách nhiệm của nhóm phát triển.

 Nhận thức được những rủi ro hệ thống tiềm tàng, vnstock chỉ chính thức cung cấp các hàm truy xuất dữ liệu riêng lẻ, việc sử dụng kết hợp các hàm để truy xuất dữ liệu hàng loạt gây tổn thất đến hệ thống của công ty chứng khoán/nguồn cấp dữ liệu nằm ngoài phạm vi chúng tôi có thể kiểm soát.