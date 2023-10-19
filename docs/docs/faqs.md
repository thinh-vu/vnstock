---
sidebar_position: 6
---

# Câu hỏi thường gặp

## Chung

### Hệ sinh thái vnstock bao gồm những gì?

Hiện tại Vnstock cung cấp các sản phẩm/kênh thông tin sau:
- Gói phần mềm python: vnstock python & vnstock web app

- Website: 

    - [![vnstock.site - Ghé thăm](https://img.shields.io/badge/vnstock.site-Ghé_thăm-4CAF50?style=for-the-badge&logo=www)](https://vnstock.site/)

- Cộng đồng và kênh thông tin: 

    - [![vnstock group - Tham gia](https://img.shields.io/badge/vnstock_group-Tham_gia-0866FF?style=for-the-badge&logo=facebook)](https://www.facebook.com/groups/vnstock)

    - [![vnstock - Tham gia](https://img.shields.io/badge/vnstock-Tham_gia-5865F2?style=for-the-badge&logo=Discord)](https://discord.gg/ruugCSWVCJ)

    - [![Vnstock - Theo dõi](https://img.shields.io/badge/Vnstock-Theo_dõi-0866FF?style=for-the-badge&logo=facebook)](https://www.facebook.com/vnstock.official)

    - [![Learn Anything - Theo dõi](https://img.shields.io/badge/Learn_Anything-Theo_dõi-FF0000?style=for-the-badge&logo=youtube)](https://www.youtube.com/@learn_anything_az)

    - [![PyPI - Download](https://img.shields.io/badge/PyPI-Download-4CAF50?style=for-the-badge&logo=pypi)](https://pypi.org/project/vnstock/)

### Cơ sở của phương pháp thu thập dữ liệu do vnstock cung cấp là gì?


Vnstock cung cấp giải pháp công nghệ sử dụng Python để thu thập dữ liệu từ các nguồn dữ liệu chứng khoán Việt Nam thông qua các APIs công khai. Nói một cách dễ hiểu, các APIs này được khám phá thông qua thủ thuật Web Scraping hay còn gọi là Reverse Engineering tức dò các APIs được website chứng khoán sử dụng để gửi/nhận dữ liệu giữa hệ thống cơ sở dữ liệu (back-end) với giao diện người dùng cuối (front-end). 

Các API này không được chia sẻ công khai kèm tài liệu hướng dẫn cho người dùng phổ thông, tuy nhiên thông qua biện pháp so sánh dữ liệu có thể dễ dàng gán nhãn và tái tạo dữ liệu thu được từ API với độ chính xác gần như tuyệt đối so với dữ liệu hiển thị trên website. 

Việc truy cập các APIs dữ liệu này là hợp pháp vì phương pháp truy cập tương đương với việc gửi/nhận dữ liệu của người dùng thông qua trình duyệt web, tuy nhiên số lượt gửi/nhận dữ liệu có thể phát sinh đột biến do người dùng gọi API liên tục thông qua lập trình do vô tình hay cố ý. 

Do đó, việc sử dụng các APIs này cần được thực hiện với tinh thần trách nhiệm và tôn trọng nguồn dữ liệu nhằm tránh gửi yêu cầu gây quá tải hệ thống của nguồn dữ liệu (công ty chứng khoán). Chúng tôi khuyên người dùng hạn chế sử dụng API hàng loạt trong khung giờ giao dịch để tránh làm ảnh hưởng đến hoạt động thường xuyên của các nhà đầu tư khác và bản thân nguồn dữ liệu. Trong thời gian tới, Vnstock sẽ nghiên cứu các giải pháp công nghệ mới nhằm tạo và lưu trữ cơ sở dữ liệu riêng để hạn chế đến mức thấp nhất ảnh hưởng tiêu cực đến nguồn dữ liệu gốc.

Về phía công ty chứng khoán, các anh chị có thể hợp tác chính thức với Vnstock để cung cấp dữ liệu chứng khoán thông qua các APIs riêng biệt cho người dùng nâng cao. Như vậy, hệ thống giao dịch cho người dùng phổ thông sẽ không bị ảnh hưởng do thao tác Web Scraping gây ra. 
Hoạt động này giúp anh chị xây dựng sự gắn kết khách hàng cá nhân với công ty mình, đồng thời thúc đẩy khách hàng cá nhân gia tăng giao dịch qua nền tảng mà công ty cung cấp bởi dữ liệu là minh bạch và dễ dàng truy cập. Giao dịch thuật toán là xu thế tất yếu của tương lai, việc người dùng tìm kiếm giải pháp xử lý dữ liệu hiệu quả và tốc độ hơn khi dùng vnstock và python là một nhu cầu thiết yếu nên được đáp ứng. Vnstock rất sẵn lòng giới thiệu thương hiệu của quý công ty tới cộng đồng người dùng và hợp tác với quý công ty trong việc xây dựng hệ sinh thái công nghệ cho khách hàng cá nhân.

Để liên hệ hợp tác, anh/chị vui lòng trao đổi qua email: support@vnstock.site


### Tại sao vnstock chọn phát triển Mã Nguồn Mở?


Khác với các sản phẩm mã nguồn đóng (closed-source), các sản phẩm mã nguồn mở (open-source) thúc đẩy tính minh bạch và cho phép phát triển phần mềm đạt chất lượng cao. Bởi tính mở, vnstock muốn chào đón những ý tưởng tốt nhất, các nhà phát triển xuất sắc nhất tham gia, và tạo nên một cộng đồng đoàn kết. 
Một cách ngắn gọn, vnstock chọn phát triển mã nguồn mở nhằm thúc đẩy sự đổi mới và đột phá trong phát triển công nghệ trong lĩnh vực tài chính tại Việt Nam. Đồng thời, vnstock cho phép bạn tùy chỉnh mã nguồn vnstock để phù hợp với nhu cầu đa dạng của mình.


### Tại sao vnstock được cung cấp miễn phí?


Chúng tôi tin rằng hoạt động nghiên cứu đầu tư nên được phổ biến với tất cả mọi người Việt Nam để tạo ra một cộng đồng thịnh vượng, một đất nước phát triển với nền dân trí tài chính ở tầm bậc cao. vnstock sưu tầm các API công khai và cung cấp tới bạn bộ dữ liệu hoàn chỉnh và miễn phí, giúp các cá nhân/tổ chức dễ dàng truy cập vào các dữ liệu tài chính hiện có mà không phải trả bất kỳ chi phí nào. Tuy nhiên, nguồn dữ liệu miễn phí cũng thể hiện một số hạn chế đến với độ tin cậy và chính xác xuất phát từ nguồn cấp dữ liệu (công ty chứng khoán). Vnstock cung cấp cho bạn dữ liệu mà các nguồn dữ liệu này hiển thị trên website của họ. Tùy từng thời điểm, nguồn dữ liệu phù hợp được lựa chọn để cung cấp cho bạn. Để phát triển dự án, chúng tôi sẽ cung cấp thêm các tùy chọn trả phí hợp lý trong thời gian tới giúp người dùng được lựa chọn nguồn dữ liệu chất lượng, tốc độ với độ tin cậy cao phục vụ cho nhu cầu đầu tư/nghiên cứu của mình. 


### Ai là người dùng của vnstock?

Qua giao lưu và tương tác với người dùng, các đối tượng người dùng chính hiện ghi nhận được bao gồm:

- **Chuyên gia dữ liệu/lập trình viên**: đây là những người có chuyên môn công nghệ và dữ liệu, là đối tượng trực tiếp sử dụng thành thạo python cho dự án của mình hoặc xây dựng sản phẩm dựa trên bộ API mà vnstock cung cấp.

- **Nhà đầu tư cá nhân**: Xu hướng giao dịch thuật toán đang phát triển nóng trong thời gian gần đây, các nhà đầu tư cá nhân tìm kiếm giải pháp công nghệ làm lợi thế giao dịch của mình và tự xây dựng hệ thống phân tích hoặc bot giao dịch để hiện thực hóa chiến lược đầu tư.

- **Sinh viên**: Sinh viên các trường đại học khối ngành kinh tế toàn quốc là một bộ phận người dùng quan trọng của vnstock. Đây cũng là nguồn lực  đổi mới, sáng tạo trong việc áp dụng công nghệ rộng rãi vào việc phát triển thị trường tài chính Việt Nam. 

    - Ở khu vực phía Nam, các trường đại học điển hình mà vnstock ghi nhận bao gồm: UEL, UEH, ĐH Tài chính Marketing, Đại học FPT
    - Ở khu vực phía Bắc, các trường đại học được ghi nhận có sinh viên sử dụng vnstock bao gồm: Đại học Bách khoa, Đại học Kinh tế quốc dân.

- **Nhà nghiên cứu**: Lĩnh vực nghiên cứu tương đối đa dạng, qua trao đổi cá nhân thì vnstock được các bạn làm công tác nghiên cứu yêu thích bởi cho phép truy cập dữ liệu hàng loạt, cập nhật dễ dàng và hoàn toàn miễn phí (phù hợp với ngân sách giới hạn).

Dù bạn là ai, làm lĩnh vực gì, vnstock muốn đồng hành với bạn cùng phát triển. Nếu có những yêu cầu đặc biệt cần được hỗ trợ hoặc góp ý phát triển sản phẩm, bạn có thể liên hệ với chúng tôi qua email: support@vnstock.site hoặc các kênh trao đổi cộng đồng. Ý kiến của bạn luôn được đón nhận và đánh giá cao.


### Tôi có phải trả phí khi sử dụng vnstock?


Vnstock được cung cấp dưới dạng phần mềm mã nguồn mở, miễn phí. Bạn được tự do sử dụng, phân phối và sửa đổi phần mềm theo các điều khoản của giấy phép MIT và các nguyên tắc của dự án. Bạn có thể tùy tâm đóng góp kinh phí phát triển và duy trì dự án tới tác giả Thịnh Vũ. Đơn giản là gửi tặng một ly cafe như việc ai đó đã giúp bạn một việc tốt và bạn muốn tri ân. 
Để phát triển dự án bền vững, trong tương lai vnstock sẽ giới thiệu thêm các sản phẩm/tính năng nâng cao có trả phí bởi không ai có thể tồn tại chỉ để cung cấp mọi thứ miễn phí và chúng tôi cũng có công việc, gia đình cần chăm lo như với bạn vậy. Tuy nhiên, vnstock phiên bản mã nguồn mở luôn miễn phí.


### Nhóm cộng đồng nào tôi nên tham gia để được hỗ trợ?
- **Kênh Discord** là cộng đồng dành cho tất cả người dùng vnstock bất kể trả phí hay miễn phí. Bạn có thể tham gia để trao đổi, nhờ trợ giúp và học hỏi lẫn nhau ở nhóm này.
- **Nhóm Facebook** dành riêng cho thành viên thân thiết, yêu cầu ủng hộ dự án 100K cho một lần duy nhất để gia nhập. Đây cũng là cách các bạn có thể gửi lời cám ơn tác giả thông qua hỗ trợ tài chính dưới dạng tặng một ly cafe. Nhóm này có ít thành viên tham gia hơn tuy nhiên hầu hết các thành viên hoạt động sôi nổi, là những người có kinh nghiệm về đầu tư hoặc hoạt động trong lĩnh vực chứng khoán. Đây là một cộng đồng chất lượng và gắn kết bởi đơn giản nhóm người dùng này hiểu được giá trị của vnstock, ủng hộ dự án và có khả năng tài chính để sẵn sàng sử dụng các sản phẩm chất lượng.

Nếu bạn chưa sẵn sàng ủng hộ dự án 100K để tham gia nhóm cũng không sao. Bạn vẫn có thể tham gia nhóm Discord để nhận hỗ trợ chung từ cộng đồng. Chúc bạn thành công!


### Làm thế nào để tham gia cộng đồng vnstock trả phí?


Để có thể tham gia cộng đồng trả phí của vnstock được tổ chức trên nền tảng Facebook, bạn vui lòng ủng hộ dự án tối thiểu 100K theo hình thức chuyển tiền Momo hoặc chuyển khoản ngân hàng như thông tin bên dưới. Sau đó bạn gửi yêu cầu tham gia nhóm và trả lời 3 câu hỏi đơn giản để được duyệt tham gia nhóm. Ngay khi nhận được báo có, admin sẽ duyệt yêu cầu của bạn ngay lập tức.

[![vnstock group - Tham gia](https://img.shields.io/badge/vnstock_group-Tham_gia-0866FF?style=for-the-badge&logo=facebook)](https://www.facebook.com/groups/vnstock)

Cám ơn bạn đã tin tưởng, đồng hành và ủng hộ dự án.



### Tôi có thể đóng góp quỹ Vnstock như thế nào?

Để đóng góp cho dự án, bạn có thể chọn chuyển khoản ngân hàng hoặc chuyển tiền qua ví điện tử Momo.

![vcb qr](assets/images/vcb-qr-thinhvu.jpg?raw=true)
![momo qr](assets/images/momo-qr-thinhvu.jpeg?raw=true)

### Quỹ Vnstock được sử dụng như thế nào?

Tác giả sử dụng quỹ Vnstock để duy trì và phát triển dự án. Cụ thể, quỹ Vnstock được sử dụng để:

- Trả chi phí duy trì máy chủ và tên miền của dự án.

- Trả chi phí nâng cấp và vận hành các dịch vụ hỗ trợ người dùng cho dự án.

- Sử dụng làm chi phí cho các hoạt động quảng bá và marketing của dự án.

- Sử dụng làm chi phí cho các hoạt động đào tạo và hỗ trợ người dùng.


### Tôi có thể yêu cầu hỗ trợ như thế nào?

Hiện tại Vnstock docs đã được hoàn thiện và cung cấp một mảnh ghép quan trọng giúp người dùng tiếp cận tài liệu và các hướng dẫn sử dụng vnstock trực quan và tối ưu. Trước khi tìm đến tác giả để nhắn tin trực tiếp, bạn vui lòng tự nghiên cứu để tiết kiệm thời gian cho cả hai bên. Tôi cũng có những công việc và ưu tiên riêng của mình và không phải lúc nào cũng sẵn sàng hỗ trợ bạn 24/4 cho những câu hỏi rất căn bản đã có trong tài liệu và việc bạn đặt câu hỏi chỉ vì mình "lười" tìm kiếm. Điều này là không thể chấp nhận được.
Nếu bạn thực sự cần hỗ trợ, đây là những cách bạn có thể làm theo thứ tự ưu tiên:

1. Hỏi trong nhóm Facebook thành viên (Ủng hộ Vnstock 100k để tham gia): [![vnstock group - Tham gia](https://img.shields.io/badge/vnstock_group-Tham_gia-4CAF50?style=for-the-badge&logo=facebook)](https://www.facebook.com/groups/vnstock)

2. Hỏi trong nhóm cộng đồng Discord (miễn phí): [![vnstock - Tham gia](https://img.shields.io/badge/vnstock-Tham_gia-5865F2?style=for-the-badge&logo=Discord)](https://discord.gg/ruugCSWVCJ)

3. Gửi email yêu cầu hỗ trợ: support@vnstock.site

4. Nhắn tin trực tiếp cho tác giả: [![Thinh Vu - Nhắn tin](https://img.shields.io/badge/Thinh_Vu-Nhắn_tin-F74F8A?style=for-the-badge&logo=messenger&logoColor=F74F8A)](https://www.messenger.com/t/mr.thinh.ueh)

