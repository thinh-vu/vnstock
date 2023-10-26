# Xuất dữ liệu

!!! abstract "Xuất file csv"
    Xuất dữ liệu ra dạng bảng tính được hỗ trợ mặc định bởi vnstock vì bản thân dữ liệu trả về khi bạn gọi hàm **vnstock** bất kỳ là các Pandas DataFrame trong Python có hỗ trợ khả năng này. **vnstock** hoạt động tốt nhất khi tích hợp với hệ sinh thái Python, tuy nhiên nếu bạn chưa sẵn sàng sử dụng Python thì vẫn có thể sử dụng dữ liệu từ vnstock cho các phần mềm quen thuộc như CSV, Excel hay Google Sheets hoặc thậm chí là lưu vào cơ sở dữ liệu. Dưới đây là cách thực hiện.

## Xuất file CSV

Khi gọi một hàm vnstock, bạn có thể gán kết quả của hàm với một biến bất kỳ và xuất ra file csv. Ví dụ với hàm lấy giá lịch sử:

```python
from vnstock import * # bỏ qua dòng này nếu đã thực hiện import
df =  stock_historical_data(symbol='GMD', 
                            start_date="2021-01-01", 
                            end_date='2022-02-25', resolution='1D', type='stock', beautify=True)
df.to_csv(r'ĐƯỜNG_DẪN_THƯ_MỤC_CỦA_BẠN/GMD.csv', index=False)
```

Trong đó:

- Bạn có thể thay thế `df` bằng tên đối tượng DataFrame bất kỳ trả về từ hàm của vnstock.
- Nếu bạn sử dụng Google Colab hoặc chạy Jupyter Notebook trên Macbook, hoặc Linux cho dự án thì đường dẫn sử dụng dấu ngăn cách `/`, ví dụ `/content/drive/MyDrive/Colab Notebooks/GMD.csv`.
- Nếu chạy dự án trên môi trường Python trong máy tính Windows, dấu ngăn cách địa chỉ thư mục là `\`, ví dụ `C:\Users\user\Downloads\GMD.csv`. Lưu ý địa chỉ thư mục cho máy tính Windows, cần sử dụng chữ `r` phía trước như trong code mẫu.

## Xuất file Excel

```python
from vnstock import * # bỏ qua dòng này nếu đã thực hiện import
df =  stock_historical_data(symbol='GMD', 
                            start_date="2021-01-01", 
                            end_date='2022-02-25', resolution='1D', type='stock', beautify=True)
df.to_excel(r'ĐƯỜNG_DẪN_THƯ_MỤC_CỦA_BẠN/GMD.xlsx', index=False)
```

Trong đó:

- Bạn có thể thay thế `df` bằng tên đối tượng DataFrame bất kỳ trả về từ hàm của vnstock.
- Nếu bạn cần sử dụng file `xls` cho bản Office 2007 trở xuống thay vì bản Office mới thì đổi đuôi file từ `xlsx` thành `.xls` trong code mẫu.

## Xuất file Google Sheets

!!! tip "Xuất file Google Sheets"
    Để xuất dữ liệu qua Google Sheets, cách đơn giản nhất là chạy notebook trên môi trường Google Colab, như vậy quá trình xác thực dịch vụ diễn ra đơn giản hơn rất nhiều so với bạn chạy từ máy cục bộ. Đọc bài hướng dẫn [Đọc và xuất dữ liệu qua Google Sheets](https://thinhvu.com/2021/05/27/doc-va-xuat-du-lieu-google-sheets-voi-python/) để biết thêm chi tiết nếu bạn cần xuất file từ máy ảo, máy cục bộ.

- Xác định đối tượng DataFrame bất kỳ cần xuất dữ liệu. Ví dụ bạn muốn xuất dữ liệu danh sách công ty niêm yết.

```python
from vnstock import *
df = listing_companies() # Gán bất hàm bất kỳ cho một biến, ví dụ df
sheet_file = 'listing_companies' # Đặt tên cho file Google Sheets (nếu tạo mới, dùng file có sẵn thì không cần)
```

- Tiếp theo cần một đoạn code để xác thực dịch vụ, cho phép Google Colab kết nối với Google Sheets.

```python
from google.colab import auth
auth.authenticate_user()

import gspread
from google.auth import default
from gspread_dataframe import set_with_dataframe

creds, _ = default()
gc = gspread.authorize(creds)from google.colab import auth
auth.authenticate_user()

import gspread
from google.auth import default
from gspread_dataframe import set_with_dataframe

creds, _ = default()
gc = gspread.authorize(creds)
```

- Đến đây, bạn có hai lựa chọn:

### Xuất vào sheet mới

```python
sh = gc.create(sheet_file)
worksheet = gc.open(sheet_file).sheet1 # Mở sheet mặc định để xuất dữ liệu, chọn 1 trong 3 tùy chọn với biến worksheet, dùng dòng nào bỏ comment dòng đó, và comment dòng không cần dùng
# worksheet = sh.add_worksheet(title="listing_companies", rows="1000", cols="20") # Tạo sheet mới để xuất dữ liệu
# worksheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1vT6o6U1dHYMdHASZNKPvmzDRhgKTvQXsZ_46CvBOpuI').sheet1  # Mở file sheet có sẵn bằng URL
set_with_dataframe(worksheet, df)
```

### Xuất vào dải ô có sẵn

```python
worksheet = gc.open(sheet_file).sheet1 # Mở sheet mặc định để xuất dữ liệu, chọn 1 trong 3 tùy chọn với biến worksheet, dùng dòng nào bỏ comment dòng đó, và comment dòng không cần dùng

cell_list = worksheet.range('A1:C2') # Chọn vùng dữ liệu trên Google Sheets bạn muốn chèn dữ liệu từ DataFrame
# Update the data in the worksheet

for cell, value in zip(cell_list, df.values.flatten()):
    cell.value = value

worksheet.update_cells(cell_list)
```
## Xuất dữ liệu cho Amibroker

!!! tip "Tải dữ liệu cho Amibroker" 
    Thực hiện tùy biến đôi chút với hàm `stock_historical_data` là bạn có thể tải dữ liệu cho Amibrokder dưới dạng file csv một cách dễ dàng. Hiện tại `vnstock` cung cấp khả năng tải dữ liệu Amibroker không giới hạn với cả dữ liệu chứng khoán, phái sinh, và chỉ số với tất cả các khung thời gian cho phép từ 1, 3, 5, 15, 30, 60 phút và dữ liệu EOD.

Hãy thử nghiệm ngay tính năng tải dữ liệu này với Vnstock Web App.




