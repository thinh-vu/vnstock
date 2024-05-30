# Vnstock3 - Giải pháp phân tích chứng khoán mở cho người Việt

<div id="logo" align="center">
    <a href="http://vnstock.site?utm_source=github&utm_medium=vnstock&utm_content=readme">
        <img src="https://raw.githubusercontent.com/thinh-vu/vnstock/main/assets/images/vnstock_bw_logo_trans_rec.png" alt="vnstock_logo"/>
    </a>
</div>

<div id="badges" align="center">
<img src="https://img.shields.io/pypi/pyversions/vnstock?logoColor=brown&style=plastic" alt= "Version"/>
<img src="https://img.shields.io/pypi/dm/vnstock" alt="Download Badge"/>
<img src="https://img.shields.io/github/last-commit/thinh-vu/vnstock" alt="Commit Badge"/>
<img src="https://img.shields.io/github/license/thinh-vu/vnstock?color=red" alt="License Badge"/>
</div>

---


# I. 🎤 Giới thiệu

`Vnstock3` là phiên bản phần mềm Vnstock thế hệ thứ 3 được giới thiệu công khai vào 10/5/2024. 
Đây là thế hệ Vnstock với nhiều nâng cấp giá trị, chia sẻ tầm nhìn rõ ràng hơn về Vnstock với vai trò một giải pháp phân tích thị trường chứng khoán mã nguồn mở mang nhiều dấu ấn của tương lai công nghệ.

Vnstock sẽ luôn là giải pháp miễn phí để bạn tiếp cận dữ liệu chứng khoán, tài chính toàn diện, miễn phí với các nhu cầu thiết yếu và làm quen với bộ giải phép Python linh hoạt. Chúc mừng bạn là một phần của sự thay đổi trong hành trình chuyển đổi số thị trường chứng khoán tại Việt Nam.

# II. ⏱️ Cập nhật đáng chú ý

- 10-05-2024: Ra mắt phiên bản Vnstock `0.3.0.1` với tên gói cài đặt `vnstock3`

Chi tiết cập nhật phần mềm và phiên bản [tại đây](https://vnstocks.com/docs/tai-lieu/lich-su-phien-ban)

# III. 📔 Tài liệu hướng dẫn

Trước khi bắt đầu, hãy đánh dấu yêu thích để giúp dự án có thể tiếp cận tới nhiều người hơn. Cám ơn bạn!

![star_project](https://raw.githubusercontent.com/thinh-vu/vnstock/beta/docs/docs/assets/images/github_star_guide.png)

Cài đặt thư viện với câu lệnh sau:

```
pip install -U vnstock3
```

Để hiểu rõ hơn về vnstock và hướng dẫn sử dụng toàn diện, bạn có thể truy cập [vnstock.site](https://vnstock.site). 

Bạn cần mở Vnstock3 từ Terminal hoặc Jupyter Notebook và nạp thư viện lần đầu cài đặt để chấp nhận điều khoản & điều kiện sử dụng trước khi tiếp tục.

```
from vnstock3 import Vnstock
```
Thông báo hiện ra, bạn chỉ cần ấn phím Enter để đồng ý. Lời nhắc này chỉ hỏi 1 lần duy nhất khi bạn cài đặt trên thiết bị lần đầu tiên.

Để bỏ qua lời nhắc và tự động chấp nhận điều khoản, bạn có thể chèn đoạn code sau vào đầu dự án của mình khi thực thi.

```
import os
if "ACCEPT_TC" not in os.environ:
    os.environ["ACCEPT_TC"] = "tôi đồng ý"
```
Chúc các bạn thành công và có nhiều trải nghiệm thú vị với Vnstock3!

<!-- [![vnstock docs - Xem Thêm](https://img.shields.io/badge/vnstock_docs-Xem_Thêm-2ea44f?style=for-the-badge&logo=Github)](https://thinh-vu.github.io/vnstock) -->

<!-- [![vnstock_docs_home](https://raw.githubusercontent.com/thinh-vu/vnstock/beta/docs/docs/assets/images/vnstock_docs_home.png)](https://thinh-vu.github.io/vnstock) -->

# IV. 🙋‍♂️ Thông tin liên hệ

Bạn có thể kết nối với tác giả qua các hình thức sau. Trong trường hợp cần hỗ trợ nhanh, bạn có thể chọn nhắn tin qua Messenger hoặc Linkedin, tôi sẽ phản hồi ngay lập tức nếu có thể trong hầu hết các trường hợp.

<div id="badges" align="center">
  <a href="https://www.linkedin.com/in/thinh-vu">
    <img src="https://img.shields.io/badge/LinkedIn-blue?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn Badge"/>
  </a>
  <a href="https://www.messenger.com/t/mr.thinh.ueh">
    <img src="https://img.shields.io/badge/Messenger-00B2FF?style=for-the-badge&logo=messenger&logoColor=white" alt="Messenger Badge"/>
  <a href="https://www.youtube.com/@learn_anything_az?sub_confirmation=1">
    <img src="https://img.shields.io/badge/YouTube-red?style=for-the-badge&logo=youtube&logoColor=white" alt="Youtube Badge"/>
  </a>
  </a>
    <a href="https://github.com/thinh-vu">
    <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="Github Badge"/>
  </a>
</div>

# V. 🔑 Giấy phép sử dụng (License)

`Vnstock3` được phát hành theo giấy phép tuỳ chỉnh hướng đến cá nhân, không dành cho mục đích thương mại. Quyền sử dụng được quy định cụ thể trong [giấy phép](LICENSE.md) kèm theo. Nếu bạn hoặc tổ chức bạn đang làm việc muốn sử dụng Vnstock có thể liên hệ tác giả để hiểu rõ phạm vi sử dụng và được cấp phép chính thức.

Khi sử dụng Vnstock trong dự án của mình, bạn cần trích dẫn thông tin về tác giả và dự án theo hướng dẫn của Vnstock.

# VI. Lịch sử lượt yêu thích

Bạn có thể hỗ trợ dự án bằng cách cực kỳ đơn giản là đánh dấu yêu thích để giúp dự án có thể tiếp cận tới nhiều người hơn. Dưới đây là lịch sử lượt yêu thích của dự án.

[![Star History Chart](https://api.star-history.com/svg?repos=thinh-vu/vnstock&type=Date)](https://star-history.com/#thinh-vu/vnstock&Date)
