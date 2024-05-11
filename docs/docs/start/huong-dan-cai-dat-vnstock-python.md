---

title: Lựa chọn phiên bản
---

# Cài đặt vnstock

## Xác định phiên bản phù hợp

!!! tip "Phiên bản"
    vnstock được phát triển thành hai nhánh riêng biệt. Trong hầu hết trường hợp bạn có thể sử dụng lệnh cài đặt nhanh từ PyPI. Nếu bạn có nhu cầu cài đặt vnstock từ mã nguồn, bạn cần chọn phiên bản phù hợp và *copy câu lệnh tương ứng để thực hiện cài đặt ở bước tiếp theo*:

1. Cài đặt nhanh, sử dụng bản vnstock ổn định được chia sẻ qua pypi.org, sử dụng câu lệnh sau:
   ```shell
   pip install --upgrade vnstock
   ```
2. Cài đặt trực tiếp từ mã nguồn có trên Github:

    - Bản `beta` (nhận cập nhật mới nhất) được chia sẻ tại nhánh `beta` của Github repo.
     ```shell
     pip install git+https://github.com/thinh-vu/vnstock.git@dev
     ```

??? info "Chọn xem nhánh phù hợp"

    ![choose a branch](../assets/images/choose_a_branch.png)

## Chạy câu lệnh cài đặt

> Khi sử dụng file [Demo Notebook](https://github.com/thinh-vu/vnstock/blob/legacy/docs/gen2_vnstock_demo_index_all_functions_testing_2023.ipynb) để bắt đầu, các câu lệnh cài đặt cần thiết đã được cung cấp sẵn để bạn thực thi (run).

`pip được sử dụng để cài đặt vnstock`. pip có sẵn trong hầu hết các bản phân phối Python được cài đặt. Phiên bản python cần thiết cho vnstock tối thiểu là 3.7. Bạn có thể paste câu lệnh đã copy ở Bước 1 và chạy nó trong môi trường Python bạn đang sử dụng.

- Jupyter Notebook/Jupyter Lab/Google Colab: Mở file demo notebook để chạy các lệnh có sẵn.
- CLI: Mở Terminal (macOS/Linux) hoặc Command Prompt (Windows Desktop) và paste dòng lệnh trên, bấm Enter để cài đặt. Lưu ý: Nếu sử dụng Windows và Python cài đặt với Anaconda thì chọn Anaconda Prompt để chạy lệnh thay vì Command Prompt mặc định.

## 🔐 Cài đặt gói thư viện nâng cao

!!! tip "Insiders Program"
	Đối với các thành viên tham gia tài trợ dự án thông qua Insiders Program, các bạn có thêm quyền truy cập vào các kho mã nguồn riêng tư (private repo). Mỗi gói cài đặt bổ sung này sẽ có hướng dẫn kèm theo trong file README của repo đó trên Github.

## Cài đặt các gói thư viện bắt buộc (gỡ lỗi)

!!! tip "Lưu ý" 
    Trong trường hợp bạn không sử dụng Google Colab là môi trường mặc định để chạy vnstock, bạn sẽ cần phải đảm bảo môi trường Python của mình có đầy đủ các gói phần mềm bắt buộc kèm theo (dependencies/requirements) để có thể chạy được `vnstock`. 

- Nếu cài Python với Anaconda, bạn có thể bỏ qua bước này.

- Nếu cài bản python thuần từ python.org hoặc Python từ Windows Store, bạn sẽ cần cài đặt thêm tối thiểu `pandas` và `requests` với công cụ `pip`.

Để quá trình cài đặt diễn ra đơn giản và suôn sẻ, bạn có thể làm theo các bước sau:

- Tải file [requirement.txt](https://github.com/thinh-vu/vnstock/blob/legacy/requirements.txt) về máy

- Mở Command Prompt / Terminal, trỏ tới thư mục chứa file `requirements.txt`, thông thường là `Downloads` bằng lệnh:

```cd  ĐỊA_CHỈ_THƯ_MỤC_CỦA_BẠN```

- Chạy lệnh sau: 

```pip install -r requirements.txt```

Như vậy là quá trình chuẩn bị để sử dụng `vnstock` đã hoàn thành. Chúc bạn thành công!