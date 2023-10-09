---
title: Cài đặt các gói thư viện bắt buộc (gỡ lỗi)
---

### Cài đặt các gói thư viện bắt buộc (gỡ lỗi)

Trong trường hợp bạn không sử dụng Google Colab là môi trường mặc định để chạy vnstock, bạn sẽ cần phải đảm bảo môi trường Python của mình có đầy đủ các gói phần mềm bắt buộc kèm theo (dependencies/requirements) để có thể chạy được **vnstock**. 
- Nếu cài Python với Anaconda, bạn có thể bỏ qua bước này.
- Nếu cài bản python thuần từ python.org hoặc Python từ Windows Store, bạn sẽ cần cài đặt thêm tối thiểu **pandas** và **requests** với công cụ **pip**.

Để quá trình cài đặt diễn ra đơn giản và suôn sẻ, bạn có thể làm theo các bước sau:
- Tải file [requirement.txt](https://github.com/thinh-vu/vnstock/blob/beta/requirements.txt) về máy
-  Mở Command Prompt / Terminal, rỏ tới thư mục chứa file **requirements.txt**, thông thường là **Downloads** bằng lệnh:

```cd  ĐỊA_CHỈ_THƯ_MỤC_CỦA_BẠN```

-  Chạy lệnh sau: 

```pip install -r requirements.txt```

Như vậy là qúa trình chuẩn bị để sử dụng **vnstock** đã hoàn thành. Chúc bạn thành công!