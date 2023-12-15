# TA-Lib

!!! abstract "Giới thiệu TA-lib"
    [TA-lib](https://ta-lib.org/) được các lập trình viên sử dụng rộng rãi trong phân tích kỹ thuật cho dữ liệu tài chính, gói phần mềm nguyên bản được viết bằng ngôn ngữ C/C++.

    [TA-lib python](https://github.com/TA-Lib/ta-lib-python) dựa trên Cython thay vì [SWIG](https://swig.org/) khó cài đặt và sử dụng như gói thư viện TA-lib nguyên bản cho phép cộng đồng sử dụng ngôn ngữ Python có thể tận dụng toàn bộ sức mạnh của TA-lib trong dự án của mình.

Dữ liệu giá lịch sử từ hàm `stock_historical_data` do vnstock cung cấp có thể sử dụng hoàn hảo với dự án tích hợp bộ công cụ TA-lib. Bạn có thể làm theo hướng dẫn dưới đây để cài đặt TA-lib và sử dụng cùng vnstock (nếu chưa thử).

## Sử dụng TA-lib với Google Colab

Mở Notebook demo để sử dụng code mẫu.

[Mở Notebook :material-rocket-launch:](https://colab.research.google.com/github/thinh-vu/vnstock/blob/beta/docs/ta_lib_colab_demo.ipynb){ .md-button }


## Môi trường local

Bạn có thể tham khảo hướng dẫn cài đặt chi tiết [tại đây](https://blog.quantinsti.com/install-ta-lib-python/)

### Cài đặt TA-Lib cho Windows

Cách đơn giản và đảm bảo cài đặt thành công TA-Lib trên máy tính Windows đó là dùng file wheel đã được build sẵn từ liên kết của đại học UCI (University of California, Irvine). Cách thực hiện như sau:

1. Bạn mở liên kết [tại đây](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib) sau đó sử dụng tính năng tìm trong trang với phím tắt `Ctrl` + `F` và tìm kiếm TA-Lib.
2. Tìm và tải phiên bản Python phù hợp bạn đang có, ví dụ 3.10 hoặc bạn phải cài đặt đúng bản Python mà TA-Lib được build sẵn tại đây hỗ trợ. Khuyến cáo không nên cài bản Python mới nhất. Ví dụ trong trường hợp này, bản TA-Lib hỗ trợ Python cao nhất là 3.10 cho bản hệ điều hành 64bit có tên: `TA_Lib-0.4.24-cp310-cp310-win_amd64.whl`. 
	![](../assets/images/tim_ban_ta-lib_phu-hop-cho-windows.png)
3. Mở thư mục `Downloads` chứa file vừa được tải về trong Terminal/Command Prompt để cài đặt. Bạn có thể mở Windows Explorer, duyệt đến thư mục `Downloads` và nhập `cmd.exe` vào thanh địa chỉ của Windows Explorer để mở Command Prompt hoặc chạy Command Prompt từ Start menu. Nhập lệnh `cd Downloads` để mở thư mục này trong giao diện dòng lệnh.
4. Chạy dòng lệnh `pip install TA_Lib-0.4.24-cp310-cp310-win_amd64.whl` để cài đặt file vừa được tải về.
Chờ trong giây lát, TA-Lib sẽ được cài đặt.

	![](../assets/images/terminal_cai_dat_ta_lib.png) 
