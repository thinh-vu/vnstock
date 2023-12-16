# SSI Fast Connect API

!!! abstract "Fast Connect API"
    SSI cung cấp bộ APIs cho phép thiết lập giao dịch tự động (FastConnect Trading) và truy xuất dữ liệu thị trường chứng khoán cơ bản (FastConnect Data) cho ngôn ngữ Python. Công cụ này hoàn toàn miễn phí, bạn có thể xin cấp quyền sử dụng bằng cách mang CCCD ra phòng giao dịch của SSI gần nhất để đăng ký và kích hoạt. 

<iframe width="1024" height="600" src="https://www.youtube.com/embed/mOT7IczFJMo?si=pSo5SUEInzWR0Vam" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

vnstock cung cấp tới các bạn các hàm được tùy biến sẵn giúp dễ dàng sử dụng mà không cần bỏ nhiều thời gian nghiên cứu và tùy biến từ demo sơ khai do SSI cung cấp. Bạn có thể sở hữu gói phần mềm tích hợp này thông qua chương trình Github Sponsor. Theo đó, bạn sẽ trở thành nhà tài trợ của vnstock để có thể truy cập và sử dụng các tính năng này được phát hành dưới dạng gói phần mềm nâng cao cho vnstock. Truy cập [trang tài trợ](https://github.com/sponsors/thinh-vu) và chọn gói phù hợp và thanh toán bằng thẻ Visa/Master để có thể sử dụng ngay hôm nay.

[Kết nối SSI với vnstock :material-rocket-launch:](https://github.com/sponsors/thinh-vu){ .md-button }

**Chia sẻ thêm:**

Để có thể sử dụng thành thạo `ssi_fc_data` và `ssi_fc_trading`, bạn cần có kinh nghiệm sử dụng Python và dành khá nhiều thời gian nghiên cứu bởi những đoạn code mẫu được cung cấp ở mức tối thiểu để bạn hình dung được API cung cấp dữ liệu gì. Dữ liệu này mặc định được in ra màn hình Terminal/Command Prompt nhưng không phải kiểu dữ liệu object để có thể sử dụng ngay. Bạn có thể xem thêm chi tiết tại [ticket](https://github.com/SSI-Securities-Corporation/python-fcdata/issues/1) tôi nhờ team Dev của SSI giải đáp. Hiện tại các issue hay trao đổi qua Github thường không được phản hồi nhanh chóng. Điểm tích cực là [tài liệu hướng dẫn](https://guide.ssi.com.vn/ssi-products/v/tieng-viet/fastconnect-data/du-lieu-streaming) đã được cập nhật chuẩn hơn sau sau khi tôi gửi phản hồi.

## Thiết lập xác thực người dùng

!!! tip "Thiết lập xác thực dịch vụ"
	Để đăng ký sử dụng API đang được cung cấp miễn phí, bạn đem theo CCCD ra phòng giao dịch SSI gặp lễ tân hoặc môi giới để được hỗ trợ kích hoạt dịch vụ. Sau mỗi 3 tháng thì dịch vụ sẽ cần gia hạn lại bằng cách gọi hotline hoặc gửi email yêu cầu.

Các bước thực hiện thiết lập xác thực người dùng để kết nối API như sau:

1. Truy cập [iBoard](https://iboard.ssi.com.vn/) của SSI, tìm mục `Dịch vụ & Tiện ích` > `Dịch vụ API` như hình minh họa bên dưới. Chọn biểu tượng chìa khóa để lấy mã xác thực. Bạn sẽ được yêu cầu cung cấp OTP được gửi qua tin nhắn (hoặc hình thức bạn đăng ký tương ứng).
	![truy cập dịch vụ API](/assets/images/quan-ly-dich-vu-api-ssi-fast-connect-api.png)
2. Sau khi xác thực OTP, màn hình tiếp theo hiện ra thông tin các mã xác thực. Bạn cần copy thông tin `ConsumerID` và `ConsumerSecret` và lưu vào file để tiếp tục các bước thiết lập tiếp theo.
	![thông tin mã bảo mật](/assets/images/ma-xac-thuc-nguoi-dung-token-key-ssi-fast-connect-api.png)
## vnstock x Fast Connect Data API

!!! abstract "Hướng dẫn sử dụng module SSI Fast Connect API trong vnstock"
	Trong hướng dẫn dưới đây, bạn sẽ làm quen với cách sử dụng module `ssi` trong `vnstock-pro-data` cho phép bạn kết nối tới API dữ liệu của SSI thông qua các hàm đã tùy biến mà vnstock cung cấp.
### Import & thiết lập xác thực

Bạn cần sử dụng một ứng dụng soạn thảo lệnh như Visual Studio Code hoặc đơn giản là notepad và tạo ra một file văn bản có tên `config.py` với nội dung như sau:

```python
auth_type = 'Bearer'
consumerID = 'ID_CỦA_BẠN'
consumerSecret = 'SECRET_CỦA_BẠN'
access_jwt = 'TOKEN_CỦA_BẠN'
url = 'https://fc-data.ssi.com.vn/'  
stream_url = 'https://fc-data.ssi.com.vn/'
```

Trong đó ID và Secret là 2 thông tin tương ứng lấy từ iBoard như hướng dẫn ở trên. Thông tin `access_jwt` token cần phải chạy lệnh trong chương trình Python để lấy. Bạn mở Terminal/Command Prompt từ thư mục chứa file config.py bằng cách gõ `cmd` vào thanh địa chỉ Windows Explorer. Mở Python trong giao diện dòng lệnh, chạy các lệnh sau:

```python
import config
from ssi_fc_data import fc_md_client , model
client = fc_md_client.MarketDataClient(config)
print(client.access_token(model.accessToken(config.consumerID, config.consumerSecret)))
```

Copy đoạn token được in ra màn hình và lưu vào file config.py tại mục `access_jwt`.

Tới đây, bạn có thể lưu file `config.py` vào một nơi bất kỳ để bảo mật, sau đó chép đường dẫn file này để thiết lập ở bước tiếp theo trong chương trình Python (file `.py` hoặc Jupyter Notebook). Đường dẫn file được thay thế đoạn `THƯ_MỤC_CHỨA_FILE_CONFIG_CỦA_BẠN`.

```python
from vnstock_data.ssi import *
import sys
sys.path.append(r'THƯ_MỤC_CHỨA_FILE_CONFIG_CỦA_BẠN') # Thay đổi đường dẫn tới thư mục chứa file config.py của bạn tại đây. Mẫu file config có trong thư mục docs của repo
import config

client = fc_md_client.MarketDataClient(config)
```
### Tải dữ liệuliệu

#### Danh sách mã chứng khoán theo sàn

Sử dụng hàm `securities_list` như sau:

```python
securities_list(market='HOSE', size=1000, page=1, client=client, config=config)
```

Trong đó:

- `client`: là đối tượng python cung cấp các phương thức kết nối tới API của SSI. `client` được định nghĩa trong bước hướng dẫn xác thực ở trên
- `config` là đối tượng python chứa các thông tin xác thực, được import vào chương trình trong bước xác thực.
- `market`: tên sàn giao dịch, nhận một trong các giá trị: `HOSE`, `HNX`, `UPCOM` cho giao dịch cơ sở hoặc `DER` cho giao dịch Phái sinh
- `size`: Số kết quả trả về cho một trang
- `page`: Số thứ tự trang. Nếu bạn muốn lấy hết tất cả mã trong một lần tra cứu thì đặt tham số `size` đủ lớn, nếu chỉ muốn lấy một phần kết quả thì chỉ định rõ `size` và `page`.

Minh họa và kết quả như sau:

```shell
>>> securities_list(market='HOSE', page=1, size=1000, client=client, config=config)

Total records: 414
    Market Symbol                                          StockName                                        StockEnName
0     HOSE    AAA                  Công ty Cổ phần Nhựa An Phát Xanh            An Phat Bioplastics Joint Stock Company
1     HOSE    AAM                    Công ty Cổ Phần Thủy Sản MeKong               Mekong Fisheries Joint Stock Company
2     HOSE    AAT        Công ty Cổ phần Tập đoàn Tiên Sơn Thanh Hóa       Tien Son Thanh Hoa Group Joint Stock Company
3     HOSE    ABR              Công ty Cổ phần Đầu tư Nhãn Hiệu Việt              Viet Brand Invest Joint Stock Company
4     HOSE    ABS     Công ty Cổ phần Dịch vụ Nông nghiệp Bình Thuận  BinhThuan Agriculture Services Joint Stock Com...
..     ...    ...                                                ...                                                ...
409   HOSE    VSI  Công ty Cổ phần Đầu tư và Xây dựng Cấp thoát nước  Water Supply Sewerage Construction and Investm...
410   HOSE    VTB               Công ty Cổ phần Viettronics Tân Bình           Viettronics Tan Binh Joint Stock Company
411   HOSE    VTO            Công ty Cổ phần Vận tải Xăng dầu VITACO                 Vietnam Tanker Joint Stock Company
412   HOSE    YBM     Công ty Cổ phần Khoáng sản Công nghiệp Yên Bái       Yen Bai Industry Mineral Joint Stock Company
413   HOSE    YEG                     Công ty Cổ phần Tập đoàn Yeah1                            Yeah1 Group Corporation

[414 rows x 4 columns]
```


#### Thông tin mã chứng khoán cụ thể

Để trích xuất thông tin một mã chứng khoán bất kỳ từ hệ thống, bạn sử dụng hàm `get_securities_details` như sau:

```python
get_securities_details(client=client, config=config, symbol='ACB', market='HOSE', page=1, pageSize=100)
```

Trong đó:

- `client`: là đối tượng python cung cấp các phương thức kết nối tới API của SSI. `client` được định nghĩa trong bước hướng dẫn xác thực ở trên
- `config` là đối tượng python chứa các thông tin xác thực, được import vào chương trình trong bước xác thực.
- `symbol`: là mã chứng khoán cần tra cứu
- `market`

```shell
>>> get_securities_details(client=client, config=config, symbol='ACB', market='HOSE', page=1, pageSize=100).T
                                                      0
Symbol                                              ACB
SymbolName          Ngân hàng Thương mại Cổ phần Á Châu
SymbolEngName          Asia Commercial Joint Stock Bank
SecType                                               S
MarketId                                           HOSE
Exchange                                           HOSE
LotSize                                             100
IssueDate
MaturityDate
FirstTradingDate
LastTradingDate
ContractMultiplier                                    0
SettlMethod                                           C
ExercisePrice                                         0
ExerciseStyle
ExcerciseRatio                                        0
ListedShare                                  3884050358
TickPrice1                                            1
TickIncrement1                                       10
TickPrice2                                        10000
TickIncrement2                                       50
TickPrice3                                        50000
TickIncrement3                                      100
ReportDate                                   15/12/2023
```

#### Lấy danh sách các mã chỉ số

```python
get_index_list(client, config, exchange='', page=1, pageSize=100)
```

Trong đó:

- `client`: là đối tượng python cung cấp các phương thức kết nối tới API của SSI. `client` được định nghĩa trong bước hướng dẫn xác thực ở trên
- `config` là đối tượng python chứa các thông tin xác thực, được import vào chương trình trong bước xác thực.
- `exchange`: sàn giao dịch (không bắt buộc điền). Trả toàn bộ dữ liệu các sàn nếu để trống.
- `page`: số thứ tự trang
- `pageSize`: Số kết quả cần lấy về tối đa cho mỗi trang.

```shell
>>> get_index_list(client, config, exchange='', page=1, pageSize=100)

        IndexCode                             IndexName Exchange
0           HNX30                                 HNX30      HNX
1        HNXIndex                              HNXIndex      HNX
2   HNXUpcomIndex                         HNXUpcomIndex      HNX
3           VN100                                 VN100     HOSE
4            VN30                                  VN30     HOSE
5           VNALL                            VNAllshare     HOSE
6          VNCOND             VNAllShare Hàng Tiêu dùng     HOSE
7          VNCONS  VNAllShare Hàng thiêu dùng thiết yếu     HOSE
8       VNDIAMOND                Vietnam Diamond Index      HOSE
9           VNENE                 VNAllShare Năng lượng     HOSE
10          VNFIN                  VNAllShare Tài chính     HOSE
11      VNFINLEAD                Vietnam Diamond Index      HOSE
12    VNFINSELECT                Vietnam Diamond Index      HOSE
13         VNHEAL          VNAllShare Chăm sóc sức khỏe     HOSE
14          VNIND                VNAllShare Công nghiệp     HOSE
15           VNIT        VNAllShare Công nghệ thông tin     HOSE
16        VNIndex                               VNINDEX     HOSE
17          VNMAT            VNAllShare Nguyên vật liệu     HOSE
18          VNMID                             VNMidcap      HOSE
19         VNREAL               VNAllShare Bất động sản     HOSE
20           VNSI                     VNStability Index     HOSE
21          VNSML                            VNSmallcap     HOSE
22          VNUTI           VNAllShare Dịch vụ tiện ích     HOSE
23          VNX50                                 VNX50     HOSE
24         VNXALL                           VNXAllshare     HOSE
```

#### Liệt kê các mã chứng khoán thuộc một mã chỉ số

```python
get_index_component(client, config, index='VN30', page=1, pageSize=100)
```

Trong đó:

- `client`: là đối tượng python cung cấp các phương thức kết nối tới API của SSI. `client` được định nghĩa trong bước hướng dẫn xác thực ở trên
- `config` là đối tượng python chứa các thông tin xác thực, được import vào chương trình trong bước xác thực.
- `index`: Mã chỉ số cần tra cứu. Lấy trong danh sách trả về từ hàm `get_index_list`.
- `page`: số thứ tự trang
- `pageSize`: Số kết quả cần lấy về tối đa cho mỗi trang.

```shell
>>> get_index_component(client, config, index='VN30', page=1, pageSize=100)
Index: VN30 - HOSE. Total 30 symbols
   StockSymbol
0          ACB
1          BCM
2          BID
3          BVH
4          CTG
5          FPT
...
25         VIC
26         VJC
27         VNM
28         VPB
29         VRE
```

#### Truy xuất dữ liệu giá lịch sử OHLCV

!!! tip "Tips"
	Với hàm `get_daily_ohlc` dưới đây trả về kết quả rất chậm so với khi bạn truy xuất dữ liệu giá từ đồ thị nến trên web. Trải nghiệm của tôi khi xuất toàn bộ dữ liệu của mã cổ phiếu REE từ năm 2000 mất hơn 30s trong khi dữ liệu tương đương được trả về bằng Public API của SSI có được trong 2s.

```python
get_daily_ohlc(client, config, symbol='REE', fromDate='01/01/2000', toDate='15/12/2023', ascending=True, page=1, pageSize=6000)
```

Trong đó:

- `client`: là đối tượng python cung cấp các phương thức kết nối tới API của SSI. `client` được định nghĩa trong bước hướng dẫn xác thực ở trên
- `config` là đối tượng python chứa các thông tin xác thực, được import vào chương trình trong bước xác thực.
- `symbol`: mã chứng khoán cần tra cứu
- `fromDate`: ngày bắt đầu báo cáo, định dạng `DD/MM/YYYY`
- `toDate`: ngày kết thúc báo cáo, định dạng `DD/MM/YYYY`
- `ascending`: True hoặc False để chọn sắp xếp kết quả theo chiều thuận/nghịch.
- `page`: số thứ tự trang
- `pageSize`: Số kết quả cần lấy về tối đa cho mỗi trang.

```shell
>>> get_daily_ohlc(client, config, symbol='REE', fromDate='01/01/2000', toDate='15/12/2023', ascending=True, page=1, pageSize=6000)

     Symbol Market TradingDate   Open   High    Low  Close  Volume             Value
0       REE   HOSE  28/07/2000   1044   1044   1044   1044    1000                 0
1       REE   HOSE  31/07/2000   1063   1063   1063   1063     300                 0
2       REE   HOSE  02/08/2000   1083   1083   1083   1083     100                 0
3       REE   HOSE  04/08/2000   1102   1102   1102   1102     200                 0
4       REE   HOSE  07/08/2000   1122   1122   1122   1122    2800                 0
...     ...    ...         ...    ...    ...    ...    ...     ...               ...
5675    REE   HOSE  11/12/2023  59200  59800  58700  58700  237000       13996810000
5676    REE   HOSE  12/12/2023  58700  59100  58300  59000  287000       16830020000
5677    REE   HOSE  13/12/2023  59200  59200  57500  57700  587800  34240060000.0002
5678    REE   HOSE  14/12/2023  58100  58400  57100  57100  278100       16003970000
5679    REE   HOSE  15/12/2023  57200  58000  56500  56700  513300  29183299999.9998

[5680 rows x 9 columns]
```

#### Dữ liệu tick OHLCV của mã chứng khoán trong ngày giao dịch (Intraday)

```python
get_intraday_ohlc(client, config, symbol='SSI', fromDate='25/07/2023', toDate='31/07/2023', page=1, pageSize=1000, ascending=True)
```

Trong đó:

- `client`: là đối tượng python cung cấp các phương thức kết nối tới API của SSI. `client` được định nghĩa trong bước hướng dẫn xác thực ở trên
- `config` là đối tượng python chứa các thông tin xác thực, được import vào chương trình trong bước xác thực.
- `symbol`: mã chứng khoán cần tra cứu
- `fromDate`: ngày bắt đầu báo cáo, định dạng `DD/MM/YYYY`
- `toDate`: ngày kết thúc báo cáo, định dạng `DD/MM/YYYY`
- `page`: số thứ tự trang
- `pageSize`: Số kết quả cần lấy về tối đa cho mỗi trang.

```shell
>>> get_intraday_ohlc(client, config, symbol='SSI', fromDate='25/07/2023', toDate='31/07/2023', page=1, pageSize=1000, ascending=True, resolution=1)

    Symbol  Value TradingDate      Time   Open   High    Low  Close  Volume
0      SSI  28650  25/07/2023  09:15:52  28700  28800  28650  28650  153400
1      SSI  28600  25/07/2023  09:16:57  28650  28650  28600  28600   15500
2      SSI  28600  25/07/2023  09:17:59  28650  28650  28600  28600   50600
3      SSI  28550  25/07/2023  09:18:56  28600  28600  28550  28550   27900
4      SSI  28600  25/07/2023  09:19:58  28600  28600  28550  28600   35500
..     ...    ...         ...       ...    ...    ...    ...    ...     ...
995    SSI  29550  31/07/2023  10:44:55  29550  29550  29500  29550  132400
996    SSI  29500  31/07/2023  10:45:53  29500  29550  29500  29500  369300
997    SSI  29400  31/07/2023  10:46:49  29500  29500  29400  29400  124900
998    SSI  29400  31/07/2023  10:47:49  29400  29450  29400  29400   69900
999    SSI  29400  31/07/2023  10:48:57  29400  29450  29400  29400   20600

[1000 rows x 9 columns]
```

#### Thông tin giao dịch theo ngày của mã chứng khoán

```python
```shell
>>> get_daily_stock_price(client, config, symbol='SSI', fromDate='25/07/2023', toDate='31/07/2023', page=1, pageSize=1000, market='')
```

Trong đó:

- `client`: là đối tượng python cung cấp các phương thức kết nối tới API của SSI. `client` được định nghĩa trong bước hướng dẫn xác thực ở trên
- `config` là đối tượng python chứa các thông tin xác thực, được import vào chương trình trong bước xác thực.
- `symbol`: mã chứng khoán cần tra cứu
- `fromDate`: ngày bắt đầu báo cáo, định dạng `DD/MM/YYYY`
- `toDate`: ngày kết thúc báo cáo, định dạng `DD/MM/YYYY`
- `page`: số thứ tự trang
- `pageSize`: Số kết quả cần lấy về tối đa cho mỗi trang.
- `market`: Sàn giao dịch, để trống nếu muốn lấy tất cả kết quả từ các sàn.

```shell
>>> get_daily_stock_price(client, config, symbol='SSI', fromDate='25/07/2023', toDate='31/07/2023', page=1, pageSize=1000, market='')

  TradingDate PriceChange PerPriceChange CeilingPrice  ... TotalTradedVol   TotalTradedValue Symbol  Time
0  31/07/2023        -100          -0.30        31800  ...       15219300  450985285000.0070    SSI  None
1  28/07/2023         300              1        31500  ...       13130200  389080050000.0010    SSI  None
2  27/07/2023         450           1.60        31000  ...       16465600       482248000000    SSI  None
3  26/07/2023         200           0.70        30800  ...       12780300  367721865000.0020    SSI  None
4  25/07/2023         100           0.30        30700  ...       14449000       415978000000    SSI  None

[5 rows x 31 columns]
```
#### Kết quả giao dịch của mã chỉ số theo ngày

Trong đó:

- `client`: là đối tượng python cung cấp các phương thức kết nối tới API của SSI. `client` được định nghĩa trong bước hướng dẫn xác thực ở trên
- `config` là đối tượng python chứa các thông tin xác thực, được import vào chương trình trong bước xác thực.
- `index`: mã chỉ số cần tra cứu
- `fromDate`: ngày bắt đầu báo cáo, định dạng `DD/MM/YYYY`
- `toDate`: ngày kết thúc báo cáo, định dạng `DD/MM/YYYY`
- `page`: số thứ tự trang
- `pageSize`: Số kết quả cần lấy về tối đa cho mỗi trang.
- `orderBy`: chọn cột dùng làm tiêu chí sắp xếp thứ tự kết quả hiển thị.
- `order`: thứ tự sắp xếp kết quả. `desc` cho sắp xếp theo chiều nghịch, `asc` cho sắp xếp theo chiều thuận.

```shell
>>> get_daily_index(client, config, index='VN30', fromDate='25/07/2023', toDate='31/07/2023', page=1, pageSize=1000, orderBy='Tradingdate', order='desc', request_id='')

  IndexId IndexValue TradingDate Change RatioChange  ... TotalDealVol  TotalDealVal   TotalVol       TotalVal TradingSession
0    VN30    1230.81  31/07/2023  18.36      1.5143  ...     31046442  727903000000  325942142  9306421000000
   C
1    VN30    1212.45  28/07/2023  12.77      1.0645  ...     17227339  570484000000  268863339  7303088000000
   C
2    VN30    1199.68  27/07/2023  -1.75     -0.1457  ...     36187850  992090000000  299632550  7938811000000
   C
3    VN30    1201.43  26/07/2023   3.42      0.2855  ...     19422282  599445000000  266954582  6817668000000
   C
4    VN30    1198.01  25/07/2023   4.87      0.4082  ...     32883479  911331000000  286220979  7918426000000
   C

[5 rows x 19 columns]
```

### Streaming dữ liệu

```
start_market_data_stream(config, channel='X-QUOTE:HCM')
```

Trong đó:

- `config` là đối tượng python chứa các thông tin xác thực, được import vào chương trình trong bước xác thực.
- `channel`: Kênh streaming, được tạo ra bằng cách kết hợp mã loại dữ liệu và mã chứng khoán/chỉ số tương ứng. 

Nhóm dữ liệu | Mã kênh | Ví dụ mẫu | Chú thích
--- | --- | --- | ---
Trạng thái Mã chứng khoán | F | `F:SSI` hoặc `F:SSI-PAN` hoặc`F:ALL` | Trả về thông tin phiên giao dịch và trạng thái giao dịch của mã chứng khoán. Các mã CK được ngăn cách nhau bởi dấu "-". Hoặc có thể nhập `ALL` để lấy thông tin room của tất cả các mã.
Dữ liệu bid/ask | `X` | `X-QUOTE:SSI` hoặc `X-QUOTE:ALL` | Dữ liệu bid/ask của mã chứng khoán. Trong đó, `ALL` thể hiện lấy dữ liệu toàn bộ các mã chứng khoán.
Dữ liệu khớp lệnh | `X` | `X-TRADE:SSI` hoặc `X-TRADE:ALL` | `ALL` thể hiện lấy dữ liệu toàn bộ các mã chứng khoán.
Dữ liệu tổng hợp của thông tin bid/ask và thông tin khớp lệnh | `X` | `X:SSI-VIC` hoặc `X:ALL` | `ALL` thể hiện lấy dữ liệu toàn bộ các mã chứng khoán. Các mã CK được ngăn cách nhau bởi dấu "-"
Dữ liệu Room nước ngoài | `R` | `R:SSI` hoặc `R:SSI-VIC` hoặc `R:ALL` | Các mã CK được ngăn cách nhau bởi dấu "-". Hoặc có thể nhập ALL để lấy thông tin room của tất cả các mã.
Dữ liệu chỉ số | `MI` | `MI:VN30` hoặc `MI:VN30-HNXindex` hoặc `MI:ALL` | Cung cấp thông tin chỉ số cập nhật của tất cả các sàn HOSE, HNX, UPCOM. Các mã CK được ngăn cách nhau bởi dấu "-". `ALL` để lấy toàn bộ thông tin các mã.
Dữ liệu OHLCV | `B` | `B:SSI`; `B:SSI-VN30` hoặc `B:ALL` | Trả về thông tin open, high, low, close, volume của các mã chứng khoán/chỉ số theo tick. Các mã CK/chỉ số được ngăn cách nhau bởi dấu "-". Hoặc có thể nhập ALL để lấy thông tin OHLCV realtime của tất cả các mã.

Dữ liệu trả về có dạng như sau:

```
>>> start_market_data_stream(config, channel='X-QUOTE:HCM')

                         0
TradingDate     15/12/2023
Time              14:45:04
Exchange              HOSE
Symbol                 HCM
RType              X-QUOTE
AskPrice1          31500.0
AskPrice2          31550.0
AskPrice3          31600.0
AskVol1           479700.0
AskVol2            39500.0
AskVol3            44400.0
BidPrice1          31350.0
BidPrice2          31250.0
BidPrice3          31200.0
BidVol1             1000.0
BidVol2             2200.0
BidVol3            10700.0
TradingSession          PT
```