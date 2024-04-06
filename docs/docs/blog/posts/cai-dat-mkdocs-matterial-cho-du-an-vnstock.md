---
date: 2023-12-17
authors:
  - thinh-vu
description: |
  Ghi chú về các thiết lập trang tài liệu với Mkdocs Matterial giúp các thành viên muốn tham gia đóng góp mã nguồn và tài liệu dự án có thể cấu hình môi trường để xem trước nội dung dễ dàng trước khi chia sẻ công khai
slug: huong-dan-thiet-lap-mkdocs-matterial
categories:
  - Hướng dẫn
tags:
  - blog
draft: false
links:
---
# Thiết lập trang tài liệu Vnstock sử dụng Mkdocs Matterial

!!! abstract "Vì sao có bài viết này?"
	Ghi chú về các thiết lập trang tài liệu với Mkdocs Matterial giúp các bạn đóng góp mã nguồn và tài liệu cho dự án có thể dễ dàng cấu hình môi trường lập trình của mình và xem trước nội dung sẽ chia sẻ trên trang tài liệu vnstock. Hoặc đơn giản là bạn muốn sử dụng MKDocs tương tự vnstocho mục đích cá nhân của mình. 



## Cài đặt môi trường

### Cài đặt Python

> MKDocs chạy bằng ngôn ngữ lập trình Python. Hãy đảm bảo rằng thiết bị bạn đang dùng đã được cài đặt [Python](https://python.org/). 

- Sử dụng môi trường Cloud: Bạn có thể chọn sử dụng dịch vụ cloud đã thiết lập sẵn môi trường để bắt đầu sử dụng dễ dàng như [Github Codespace](https://github.com/features/codespaces), [Gitpod](https://www.gitpod.io/). Xem thêm hướng dẫn [tại đây](https://learn-anything.vn/kien-thuc/python/thiet-lap-moi-truong-python/#ide-hoan-chinh).
- Nếu sử dụng Windows, lời khuyên cho bạn là cài đặt Python từ Microsoft Store thay vì tải trực tiếp từ python.org. 
- Nếu bạn sử dụng Anaconda trên Windows, đảm bảo rằng bạn chọn Anaconda Prompt làm cửa sổ lệnh để chạy các lệnh ở bước tiếp theo.

<!-- more -->
### Cài đặt gói phụ thuộc

> Thư mục MKDocs của vnstock được đặt tại thư mục `vnstock/docs` của dự án.

Để cài đặt các gói phụ thuộc cần thiết để chạy thử và xem trước trang tài liệu, bạn thực hiện các bước sau:

1. Từ Command Prompt/Terminal, chuyển đến thư mục `/vnstock/docs`. Bạn cần copy/paste địa chỉ thư mục tương ứng trên máy tính của bạn.
2. Chạy lệnh sau để cài đặt với pip: `pip install -r requirements.txt`

Các bước cài đặt sẽ được thực hiện trong khoảng 30s. Bạn có thể được yêu cầu nâng cấp `pip` trước khi chạy lệnh trên nếu pip đã ra mắt phiên bản mới.

## Xem trước trang tài liệu

!!! tip "Giới thiệu"
    Tính năng xem trước (live preview) cho phép bạn xem các thay đổi thể hiện trực tiếp qua trình duyệt web từ môi trường localhost mỗi khi bạn thực hiện thay đổi với cấu hình và nội dung trang tài liệu. Việc này cho phép bạn phát hiện ra lỗi và tùy chỉnh một cách nhanh chóng thay vì phải chia sẻ công khai các thay đổi để xem.

1. Mở terminal/command prompt từ thư mục `vnstock/docs`, chạy lệnh sau `mkdocs serve`
2. Mở trình duyệt tại địa chỉ `http://127.0.0.1:8000/` để xem trang tài liệu.

<figure markdown>
  ![Giao diện làm việc với MKDocs từ Github Codespace](https://docs.vnstock.site/assets/images/mkdocs-live-preview-github-codespace.png)
  <figcaption>Giao diện làm việc với MKDocs từ Github Codespace</figcaption>
</figure>

## Cấu trúc trang tài liệu

!!! abstract "Giới thiệu"
    Dưới đây là cấu trúc cây thư mục của trang tài liệu Vnstock tương ứng với các mục trên thanh điều hướng và mô tả nội dung chi tiết để bạn có thể hiểu được để bắt đầu dễ dàng.

```
docs/
├─start/
│ ├─tai-nguyen-quan-trong-vnstock-website.md
│ ├─huong-dan-su-dung-nhanh-vnstock.md
│ └─huong-dan-cai-dat-vnstock-python.md
├─functions/
│ ├─fundamental.md
│ ├─market.md
│ ├─ratio.md
│ ├─listing.md
│ ├─chart.md
│ ├─rating.md
│ ├─financial.md
│ ├─export.md
│ ├─screener.md
│ ├─funds.md
│ ├─comparison.md
│ ├─technical.md
│ └─evaluation.md
├─integrate/
│ ├─huggingface.md
│ ├─messaging.md
│ ├─dnse_api.md
│ ├─backtesting.md
│ ├─ta_lib.md
│ ├─web_app.md
│ ├─google_sheets.md
│ ├─pytesseract-ocr-chuyen-doi-tai-lieu-tai-chinh-scan-sang-van-ban.md
│ ├─amibroker.md
│ └─ssi_fast_connect_api.md
├─insiders-program/
│ └─gioi-thieu-chuong-trinh-vnstock-insiders-program.md
├─community/
│ ├─contribute.md
│ ├─tai-tro-du-an-vnstock.md
│ ├─support.md
│ ├─vnstock-contributors-thanh-vien-tich-cuc.md
│ ├─feedback.md
│ ├─join.md
│ └─lan-toa-trai-nghiem-voi-vnstock.md
└─faq/
│ ├─feature.md
│ ├─ung-ho-du-an-vnstock.md
│ ├─community.md
│ └─vnstock-ho-tro-nguoi-dung.md
├─changes_log.md
├─course.md
├─trich-dan-va-giay-phep-su-dung-vnstock.md
└─disclaimer.md
├─assets/
│ └─images/
├─material/
│ └─overrides/
├─stylesheets/
│ └─extra.css
├─requirements.txt
```
