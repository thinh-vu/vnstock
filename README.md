# Vnstock3 - Giải pháp phân tích chứng khoán mở cho người Việt

[![Vnstock Homepage](assets/images/vnstock-hero-banner.png)](https://vnstocks.com/)

<div id="badges" align="center">
    <img src="https://img.shields.io/pypi/pyversions/vnstock?logoColor=brown&style=flat" alt="Version"/>
    <img src="https://img.shields.io/github/last-commit/thinh-vu/vnstock?style=flat" alt="Commit Badge"/>
    <img src="https://img.shields.io/badge/license-Custom%20License-red?style=flat" alt="Custom License Badge"/>
</div>

<div id="badges" align="center">
    <a href="https://pypi.org/project/vnstock/">
        <img src="https://img.shields.io/pypi/dm/vnstock?label=vnstock%20download&style=flat" alt="vnstock download badge"/>
    </a>
    <a href="https://pypi.org/project/vnstock3/">
        <img src="https://img.shields.io/pypi/dm/vnstock3?label=vnstock3%20download&style=flat" alt="vnstock3 download badge"/>
    </a>
</div>

---


# I. 🎤 Giới thiệu

`Vnstock3` là phiên bản phần mềm Vnstock thế hệ thứ 3 được giới thiệu công khai vào 10/5/2024. 
Đây là thế hệ Vnstock với nhiều nâng cấp giá trị, chia sẻ tầm nhìn rõ ràng hơn về Vnstock với vai trò một giải pháp phân tích thị trường chứng khoán mã nguồn mở mang nhiều dấu ấn của tương lai công nghệ.

Vnstock sẽ luôn là giải pháp miễn phí để bạn tiếp cận dữ liệu chứng khoán, tài chính toàn diện, miễn phí với các nhu cầu thiết yếu và làm quen với bộ giải phép Python linh hoạt. Chúc mừng bạn là một phần của sự thay đổi trong hành trình chuyển đổi số thị trường chứng khoán tại Việt Nam.

Tham gia cộng đồng Vnstock để chia sẻ, thảo luận và giao lưu cùng chúng tôi!

<div id="badges" align="center">
  <a href="https://www.facebook.com/groups/vnstock.official" target="_blank">
    <img src="https://img.shields.io/badge/Tham%20gia%20cộng%20đồng-Vnstock-blue?style=for-the-badge&logo=facebook" alt="Tham gia cộng đồng Vnstock Badge"/>
  </a>
</div>

# II. ⏱️ Cập nhật đáng chú ý

- 02-11-2024: Ra mắt Vnstock3 phiên bản 3.0.9. Chi tiết: [tại đây](https://vnstocks.com/docs/tai-lieu/lich-su-phien-ban#02-11-2024)
- 10-05-2024: Ra mắt phiên bản Vnstock `3.0.1` với tên gói cài đặt `vnstock3`

Chi tiết cập nhật phần mềm và phiên bản [tại đây](https://vnstocks.com/docs/tai-lieu/lich-su-phien-ban)

# III. 📔 Tài liệu hướng dẫn

Trước khi bắt đầu, hãy đánh dấu yêu thích để giúp dự án có thể tiếp cận tới nhiều người hơn. Cám ơn bạn!

![star_project](https://raw.githubusercontent.com/thinh-vu/vnstock/beta/docs/docs/assets/images/github_star_guide.png)

Cài đặt thư viện với câu lệnh sau:

```
pip install -U vnstock3
```

Để hiểu rõ hơn về vnstock và hướng dẫn sử dụng toàn diện, bạn có thể truy cập [vnstocks.com](https://vnstocks.com/docs/category/s%E1%BB%95-tay-h%C6%B0%E1%BB%9Bng-d%E1%BA%ABn). 

Bạn cần nạp thư viện vào môi trường Python thông qua giao diện Jupyter Notebook hoặc Terminal để có thể gọi và sử dụng các hàm được cung cấp.

```
from vnstock3 import Vnstock
stock = Vnstock().stock(symbol='VCI', source='VCI')
stock.quote.history(start='2020-01-01', end='2024-05-25')
```

<div id="badges" align="center">
  <a href="https://vnstocks.com/docs/tai-lieu/huong-dan-nhanh" target="_blank">
    <img src="https://img.shields.io/badge/Tài%20liệu%20hướng%20dẫn-Vnstock-blue?style=for-the-badge&logo=book" alt="Tài liệu hướng dẫn Vnstock Badge"/>
  </a>
</div>

# IV. Tính năng nổi bật

> `Vnstock3` cung cấp bộ dữ liệu phong phú cho nhà đầu tư, nhà phân tích và nhà nghiên cứu tài chính, giúp tiếp cận thị trường Việt Nam & Thế Giới một cách toàn diện và nhanh chóng:

1. **Dữ liệu cổ phiếu**: Giá thời gian thực, lịch sử và các chỉ số tài chính của cổ phiếu niêm yết.
2. **Chỉ số Index**: Theo dõi hiệu suất các chỉ số chính của thị trường.
3. **Chứng quyền**: Thông tin giá cả, ngày đáo hạn và nhà phát hành.
4. **Kim loại quý**: Dữ liệu giá vàng.
5. **Hợp đồng tương lai**: Giá và thông tin về hợp đồng tương lai.
6. **Quỹ đầu tư**: Thông tin quỹ mở, ETF và các quỹ đầu tư khác.
7. **Trái phiếu**: Thông tin & dữ liệu giao dịch Trái phiếu chính phủ, doanh nghiệp.
8.  **Forex**: Tỷ giá ngoại hối theo thời gian thực.
10. **Crypto**: Giá cả và giao dịch tiền điện tử.
11. **Tin tức & sự kiện**: Cập nhật tin tức tài chính và các sự kiện quan trọng.

# V. 🙋‍♂️ Thông tin liên hệ

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

# VI. 🔑 Giấy phép sử dụng (License)

`Vnstock3` được phát hành theo giấy phép tuỳ chỉnh hướng đến cá nhân, không dành cho mục đích thương mại. Quyền sử dụng được quy định cụ thể trong [giấy phép](LICENSE.md) kèm theo. Nếu bạn hoặc tổ chức bạn đang làm việc muốn sử dụng Vnstock có thể liên hệ tác giả để hiểu rõ phạm vi sử dụng và được cấp phép chính thức.

Khi sử dụng Vnstock trong dự án của mình, bạn cần trích dẫn thông tin về tác giả và dự án theo hướng dẫn của Vnstock.

# VI. Lịch sử lượt yêu thích

Bạn có thể hỗ trợ dự án bằng cách cực kỳ đơn giản là đánh dấu yêu thích để giúp dự án có thể tiếp cận tới nhiều người hơn. Dưới đây là lịch sử lượt yêu thích của dự án.

![Star History Chart](https://api.star-history.com/svg?repos=thinh-vu/vnstock&type=Date)](https://star-history.com/#thinh-vu/vnstock&Date)
