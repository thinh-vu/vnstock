# Bộ chỉ số tài chính

!!! tip "Lưu ý"
    Để tiện theo dõi và tra cứu, trong một số trường hợp chúng tôi sẽ xoay DataFrame trả về từ hàm với với phép `transpose` để thấy đầy đủ thông tin dễ hơn. Với các câu lệnh có phần kết thúc với `.T` tức là đang áp dụng phép `transpose` này.

![](../assets/images/financial_ratio.png)

Bộ chỉ số tài chính do TCBS cung cấp có thể được trích một cách dễ dàng để có toàn bộ thông tin phân tích như bạn thấy trên giao diện website TCBS bằng câu lệnh:

```python
financial_ratio(symbol="TCB", report_range='yearly', is_all=False)
```

Trong đó:
- `symbol` là mã chứng khoán bạn muốn phân tích
- `report_range` nhận 1 trong 2 giá trị: `yearly` cho phép trả về chỉ số theo năm, `quarterly` trả về dữ liệu theo quý
- `is_all` có giá trị mặc định là `True` cho phép lấy chỉ số qua tất cả các kỳ (năm hoặc quý), `False` cho phép lấy các kỳ gần nhất (5 năm hoặc 10 quý gần đây). Đây là tham số tùy chọn, nếu bạn không chỉ rõ, nó sẽ nhận giá trị mặc định là `False` tức rút gọn báo cáo để lấy 5 năm hoặc 10 quý gần nhất.

Kết quả:

```shell
>>> financial_ratio('TCB', 'yearly')
year                      2022   2021   2020   2019   2018
ticker                     TCB    TCB    TCB    TCB    TCB
priceToEarning             4.5    9.7    9.0    8.2   10.7
priceToBook                0.8    1.9    1.5    1.3    1.8
roe                      0.197  0.217  0.181  0.178  0.215
roa                      0.032  0.036   0.03  0.029  0.029
earningPerShare           5729   5132   3504   2869   2410
bookValuePerShare        32248  26452  21214  17679  14749
interestMargin           0.053  0.057  0.049  0.043  0.041
nonInterestOnToi         0.259   0.28  0.307  0.323  0.379
badDebtPercentage        0.007  0.007  0.005  0.013  0.018
provisionOnBadDebt       1.573  1.629   1.71  0.948  0.851
costOfFinancing          0.028  0.022  0.031  0.038  0.041
equityOnTotalAsset       0.162  0.164   0.17  0.162  0.161
equityOnLoan              0.27  0.268  0.269  0.269  0.324
costToIncome             0.328  0.301  0.319  0.347  0.318
equityOnLiability          0.2    0.2    0.2    0.2    0.2
epsChange                0.116  0.465  0.221  0.191  0.313
assetOnEquity              6.2    6.1    5.9    6.2    6.2
preProvisionOnToi        0.537  0.554  0.542   0.52  0.542
postTaxOnToi               0.5  0.497  0.465  0.485  0.462
loanOnEarnAsset          0.684  0.665  0.681  0.649  0.537
loanOnAsset              0.602  0.611  0.631  0.602  0.498
loanOnDeposit            1.173  1.104    1.0  0.998  0.794
depositOnEarnAsset       0.583  0.603   0.68  0.651  0.676
badDebtOnAsset           0.004  0.004  0.003  0.008  0.009
liquidityOnLiability     0.347  0.382  0.372  0.411  0.531
payableOnEquity            5.2    5.1    4.9    5.2    5.2
cancelDebt               0.002  0.004  0.013  0.002  0.008
bookValuePerShareChange  0.219  0.247    0.2  0.199  0.923
creditGrowth             0.211  0.252  0.202  0.443 -0.006
```