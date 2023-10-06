---
title: Tài nguyên quan trọng
sections:
  - Website chính thức của vnstock
  - vnstock Web app
  - Notebook minh hoạ
  - Docstring
  - vnstock cho Google Sheets
  - Lộ trình phát triển
---

Trước khi bắt đầu, bạn có thể xem Video giới thiệu chính thức cho vnstock mình mới chia sẻ trên Youtube tại đây:

<iframe width="1068" height="600" src="https://www.youtube.com/embed/6kP2TTtEY9Y?si=EOe0aW8cpqLyCnw5" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

### Website chính thức của vnstock
vnstock đã hoàn thiện bước đầu việc xây dựng một website chuyên biệt để cập nhật thông tin về dự án, tài liệu sử dụng, blog, khóa học, và các tài nguyên hữu ích khác. Các nội dung của website đang từng bước được cập nhật và hoàn thiện.

Bạn có thể truy cập [vnstock.site](https://vnstock.site?utm_source=vnstock-docs&utm_medium=resource) để biết thêm chi tiết.

Bạn cũng có thể truy cập vnstock Web app dưới đây được nhúng trên website của vnstock để người dùng tiện tìm và sử dụng.

### vnstock Web app

vnstock Web app đã được giới thiệu lần đầu vào 4/9/2023 nhằm giúp người dùng phổ thông có thể tiếp cận với vnstock theo cách đơn giản và thuận tiện nhất dù cho bạn không có bất cứ kỹ năng hay hiểu biết về lập trình python để sử dụng. 

vnstock web app được xây dựng bằng streamlit framework, sử dụng ngôn ngữ Python hoàn toàn. Đây  cũng là một định hướng rất triển vọng trong việc xây dựng các ứng dụng web trong việc phân tích chứng khoán với giao diện người dùng thân thiện và dễ sử dụng, bảo trì.

👉 Bạn có thể truy cập vnstock Web app để trải nghiệm ngay. 

[*&nbsp;*{: .fa .fa-eye} Vnstock Web App](https://vnstock.site/vnstock-app?utm_source=vnstock-docs&utm_medium=resource){: .btn .btn-cta .btn-primary}

### Notebook minh hoạ

[*&nbsp;*{: .fa .fa-eye} Demo Notebook](https://github.com/thinh-vu/vnstock/blob/beta/docs/gen2_vnstock_demo_index_all_functions_testing_2023.ipynb){: .btn .btn-cta .btn-primary}

👉 Bạn có thể mở tệp Jupyter Notebook để dùng thử tất cả các hàm của vnstock. Để sử dụng, nhấp vào nút ![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg) ở đầu trang của notebook để mở với Google Colab.

### Docstring
Tất cả các hàm của vnstock đều được cung cấp docstring đầy đủ trong khi file README.md này có thể không cập nhật toàn bộ mô tả về các tham số cho phép của từng hàm. Bạn có thể xem phần gợi ý khi viết câu lệnh trên các IDE như Google Colab, Visual Studio Code, hay Jupyter Notebook hoặc mở phần source code của Github để xem chi tiết. Trong thời gian tới, vnstock sẽ được bổ sung mô tả đầy đủ tại README.md khi có thể.

- **Docstring trên Google Colab**: Gợi ý cú pháp hàm được hiển thị khi viết bất kỳ hàm nào thuộc vnstock, trong ví dụ này hiển thị trong giao diện Google Colab.

  <div class="docstring_ide">
   <a href="assets/images/docstring_suggestion.jpeg?raw=true" data-title="Docstring trong Python IDE" data-toggle="lightbox"><img class="img-responsive" src="assets/images/docstring_suggestion.jpeg?raw=true" alt="screenshot" /></a>
   <a class="mask" href="assets/images/docstring_suggestion.jpeg?raw=true" data-title="Docstring trong Python IDE" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
  </div>

- **Docstring trong mã nguồn**: Mở mã nguồn Github tại thư mục vnstock, tìm hàm bạn cần tra cứu docstring.

  <div class="docstring_source">
   <a href="assets/images/docstring_source_code.png?raw=true" data-title="Docstring trong mã nguồn" data-toggle="lightbox"><img class="img-responsive" src="assets/images/docstring_source_code.png?raw=true" alt="screenshot" /></a>
   <a class="mask" href="assets/images/docstring_source_code.png?raw=true" data-title="Docstring trong mã nguồn" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
  </div>

### vnstock cho Google Sheets

Tôi cung cấp một hàm tùy biến làm mẫu giúp bạn hình dung và bắt đầu tùy biến các hàm python được cung cấp bởi vnstock sang ngôn ngữ Google Apps Script và sử dụng để lấy dữ liệu trên Google Sheets. Bạn có thể bắt đầu đóng góp vào source code này giúp vnstock hoàn thiện đầy đủ các tính năng cho Google Sheets và lan tỏa tới cộng đồng.

- Để sử dụng thử đoạn code trên cho việc lấy dữ liệu, bạn làm như sau:
  - Mở file [source code vnstock_gg_sheet](https://githubusercontent.com/thinh-vu/vnstock/beta/vnstock_gg_sheet/vnstock._appscript.js) và copy đoạn code.
  - Mở hoặc tạo 1 file Google Sheets bất kỳ
  - Từ menu của Google Sheets, tìm mục Extension (tiện ích mở rộng) > Apps Script như trong hình. 
  
  <div class="google_apps_script_menu">
   <a href="assets/images/google_sheet_appscript_menu.png?raw=true" data-title="Mở Google Apps Script từ Menu" data-toggle="lightbox"><img class="img-responsive" src="assets/images/google_sheet_appscript_menu.png?raw=true" alt="screenshot" /></a>
   <a class="mask" href="assets/images/google_sheet_appscript_menu.png?raw=true" data-title="Mở Google Apps Script từ Menu" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
  </div>

  - Trong giao diện Apps Script Editor, xóa hết code hiện tại và ghi đè với đoạn code bạn copy từ source code ở trên 
  

- Mở rộng để xem ảnh minh họa trên Google Apps Script

  <div class="vnstock_apps_script">
   <a href="assets/images/vnstock_google_sheets_appscript_code.png?raw=true" data-title="vnstock apps script" data-toggle="lightbox"><img class="img-responsive" src="assets/images/vnstock_google_sheets_appscript_code.png?raw=true" alt="screenshot" /></a>
   <a class="mask" href="assets/images/vnstock_google_sheets_appscript_code.png?raw=true" data-title="vnstock apps script" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
  </div>
  
- Save file (Ctrl/Cmd + S) để lưu thay đổi.
- Chuyển qua Google Sheets, bạn đã có thể nhập các tham số cho hàm và sử dụng như bình thường. Ví dụ: `= derivativesOhlc("VN30F1M", "2023-06-01", "2023-09-26", "15")`
- Đây là kết quả bạn sẽ nhận được:

  <div class="vnstock_sheets">
   <a href="assets/images/vnstock_google_sheet_result.png?raw=true" data-title="vnstock google sheets" data-toggle="lightbox"><img class="img-responsive" src="assets/images/vnstock_google_sheet_result.png?raw=true" alt="screenshot" /></a>
   <a class="mask" href="assets/images/vnstock_google_sheet_result.png?raw=true" data-title="vnstock google sheets" data-toggle="lightbox"><i class="icon fa fa-search-plus"></i></a>
  </div>

- Để chuyển đổi các hàm python hiện tại do vnstock cung cấp, bạn có thể sử dụng công cụ ChatGPT để thực hiện. Bạn sẽ cần có chút kiến thức về JavaScript để có thể tùy biến các hàm này nhanh chóng. Nếu không sẽ cần kỹ năng prompt engineering tốt để có thể yêu cầu AI hỗ trợ. Xa hơn, khi có nguồn lực, tôi sẽ cung cấp Add-in cho Google Sheets để các bạn có thể sử dụng dễ dàng hơn. Bạn có thể xem video hướng dẫn dưới đây để hiểu cách dùng ChatGPT hỗ trợ chuyển đổi hàm Python sang JavaScript.

<iframe width="1068" height="600" src="https://www.youtube.com/embed/w4GCFZUpsEY?si=r77JMNc2p-SUihI5" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

### Lộ trình phát triển

🔥 Bạn có thể tham khảo thêm [Ý tưởng cho các tính năng nâng cao cho các phiên bản sắp tới](https://github.com/users/thinh-vu/projects/1/views/4) để đồng hành cùng vnstock.