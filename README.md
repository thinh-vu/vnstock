<h2 align="center">Vietnam Stock Market data extraction from TCBS & SSI with Python</h2>

---
<div id="badges" align="center">
<img src="https://img.shields.io/pypi/pyversions/vnstock?logoColor=brown&style=plastic" alt= "Version"/>
<img src="https://img.shields.io/pypi/dm/vnstock" alt="Download Badge"/>
<img src="https://img.shields.io/github/last-commit/thinh-vu/vnstock" alt="Commit Badge"/>
<img src="https://img.shields.io/github/license/thinh-vu/vnstock?color=red" alt="License Badge"/>
</div>

vnstock is a Python package to retrieve the Vietnam stock market data from [TCBS](https://tcbs.com.vn) and [SSI]('https://iboard.ssi.com.vn/').

vnstock allows the user to download historical, intraday stock data and market insights from [TCBS](https://tcbs.com.vn).

vnstock is relying on public/private APIs to provide stock data. It is **FREE** and has **NO LIMITATIONS**.

👉 You can get more context and a demo notebook of using this package on my blog post available in Vietnamses/English [here](https://thinhvu.com/2022/09/22/vnstock-api-tai-du-lieu-chung-khoan-python/)


# I. 🛠 Installation

To get this package working, you will need to **install it via pip** (with a Python 3.7 version or higher) on the terminal by typing:

``$ pip install vnstock``

Additionally, **if you want to use the latest `vnstock` version instead of the stable one, you can install it from source** with the following command:

``$ pip install git+https://github.com/thinh-vu/vnstock.git@main``

**The master branch ensures the user that the most updated version will always be working and fully operative** so as not to wait until the 
the stable release comes out (which eventually may take some time depending on the number of issues to solve).

---

# II. 💻 Usage
You can understand some basic functionality of the vnstock package by following this guide.
First of all, you need to import the vnstock package to your python project by running this code. After that, feel free to call any functions listed below.
```python
from vnstock import *
```

## 2.1 📰 All listing companies
```python
listing_companies()
```

<details>
  <summary>Output</summary>

```
     ticker  group_code                                       company_name            company_short_name
0       HSV  UpcomIndex                   Công ty Cổ phần Gang Thép Hà Nội              Gang Thép Hà Nội
1       SCV  UpcomIndex                      Công ty Cổ phần Muối Việt Nam                  Visalco.,JSC
2       LYF  UpcomIndex              Công ty Cổ phần  Lương Thực Lương Yên  Công ty Lương Thực Lương Yên
3       CST  UpcomIndex                 Công ty Cổ phần Than Cao Sơn - TKV            Than Cao Sơn - TKV
4       BVL  UpcomIndex                            Công ty Cổ phần BV Land                       BV Land
```

</details>

## 2.2. Ticker overview
```python
ticker_overview('TCB')
```

<details>
  <summary>Output</summary>

  ```
  >>> ticker_overview('TCB')
    exchange    shortName  industryID industryIDv2   industry  ... deltaInMonth deltaInYear  outstandingShare  issueShare  ticker
  0     HOSE  Techcombank         289         8355  Ngân hàng  ...       -0.027      -0.038            3510.9      3510.9     TCB
  ```

</details>

## 2.3. 📈 Historical Data Retrieval

vnstock allows the user to **download stock historical data from TCBS**. In 
the example presented below, the historical data from the past years of a stock is retrieved. 

```python
df =  stock_historical_data(symbol='GMD', 
                            start_date="2021-01-01", 
                            end_date='2022-02-25'))
print(df.head())
```
You can also try the short form of every function in this library, for example:

```python
df = stock_historical_data("GMD", "2021-01-01", "2022-02-25")
print(df.head())
```
The result should look like this:

<details>
  <summary>Output</summary>

  ```{r, engine='python', count_lines}
          open     high      low    close   volume tradingDate
  0    32182.0  33157.0  31987.0  32279.0  4226500  2021-01-04
  1    32279.0  33596.0  31938.0  32962.0  4851900  2021-01-05
  2    33352.0  33352.0  32279.0  32572.0  3641300  2021-01-06
  3    32864.0  33644.0  31694.0  33157.0  5753700  2021-01-07
  4    33547.0  33937.0  32669.0  33059.0  4587500  2021-01-08
  ```

</details>

## 2.4. 📊 Price Table
You can download the price board of a target list of stocks to analyze with ease compared to viewing it directly on TCBS.

<details>
  <summary>Price Board</summary>

  ![price_board](./src/tcbs_trading_board_sector.png)

</details>

All you need to do is pass the list of stock symbols to the function as below:

```
price_board('TCB,SSI,VND')
```

<details>
  <summary>Output</summary>

```
>>> price_board('TCB,SSI,VND')
  Mã CP  Giá Khớp Lệnh  KLBD/TB5D  T.độ GD  KLGD ròng(CM)  ...  vnid1m  vnid3m  vnid1y  vnipe    vnipb
0   TCB        48600.0        0.6     0.49         -23200  ...    -3.7    -2.0    22.4  17.99  2.46159
1   SSI        43300.0        0.5     0.50        -112200  ...    -3.7    -2.0    22.4  17.99  2.46159
2   VND        32600.0        0.7     0.68          37300  ...    -3.7    -2.0    22.4  17.99  2.46159
```
</details>

## 2.5. 🔥 Intraday Trading Data

<details>
  <summary>Intraday view on TCBS</summary>

  ![intraday](./src/tcbs_intraday_screen1.png)
  ![intraday](./src/tcbs_intraday_screen2.png)

</details>
vnstock allows the user to **download intraday real-time/historical data**. In 
the example presented below, you can see the intraday historical data from the last weekday of the current week.

```python
df =  stock_intraday_data(symbol='GMD', 
                            page_num=0, 
                            page_size=5000))
print(df.head())
```

<details>
  <summary>Output</summary>

  ```{r, engine='python', count_lines}
  p     volume       cp       rcp   a   ba   sa     hl  pcp      time
  0     50700.0  169700  0.0  0.0      0.0  0.0   True  0.0  14:45:08
  1     50800.0    1000  0.0  0.0  BU  0.0  0.0  False  0.0  14:30:05
  2     50800.0     500  0.0  0.0  BU  0.0  0.0  False  0.0  14:30:05
  3     50800.0   20000  0.0  0.0  BU  0.0  0.0   True  0.0  14:29:54
  4     50700.0     300  0.0  0.0  SD  0.0  0.0  False  0.0  14:29:53
  ```

</details>

## 2.6. 💰Financial Ratio
### 2.6.1. Report from SSI
```python
financial_ratio_compare (symbol_ls=['TCB', 'CTG', 'BID'], industry_comparison='true', frequency= 'Yearly', start_year=2020)
```
- _symbol_ls_: a list of ticker that needs to be compared
- _industry_comparison_: `true` or `false`
- _frequency:_ `Yearly` or `Quarterly`

<details>
  <summary>Output</summary>

```
                                  Chỉ số          2017          2018          2019          2020          2021
0                                    P/E           NaN           NaN           NaN           NaN           NaN
1                                    BID  1.931659e+01  1.579755e+01  2.156374e+01  2.392118e+01  2.109997e+01
2                                    TCB  1.589460e+01  1.099041e+01  7.712361e+00  1.110489e+01  9.790559e+00
3                                    CTG  1.578063e+01  1.476715e+01  1.015345e+01  1.031625e+01  1.135594e+01
4                                    BID  1.931659e+01  1.579755e+01  2.156374e+01  2.392118e+01  2.109997e+01
..                                   ...           ...           ...           ...           ...           ...
171                           Toàn ngành  2.272894e+10  2.932384e+10  3.172492e+10  3.927128e+10  5.101939e+10
172                                  NaN           NaN           NaN           NaN           NaN           NaN
173                                  NaN           NaN           NaN           NaN           NaN           NaN
174  Dữ liệu được cung cấp bởi FiinTrade           NaN           NaN           NaN           NaN           NaN
175                https://fiintrade.vn/           NaN           NaN           NaN           NaN           NaN
```
</details>

### 2.6.2. Report from TCBS
```python
financial_ratio("TCB", 'quarterly', True)
```

<details>
  <summary>Output</summary>

  ```
  ticker  quarter  year  priceToEarning  priceToBook valueBeforeEbitda dividend  ...  badDebtOnAsset  liquidityOnLiability payableOnEquity cancelDebt ebitdaOnStockChange bookValuePerShareChange  creditGrowth
  0     TCB        4  2021             9.9          1.9              None     None  ...           0.004                 0.382             5.1      0.004                None                   0.053         0.252
  1     TCB        3  2021            10.0          2.0              None     None  ...           0.003                 0.405             5.1      0.004                None                   0.053         0.392
  2     TCB        2  2021            11.4          2.2              None     None  ...           0.002                 0.370             5.0      0.008                None                   0.061         0.353
  3     TCB        1  2021             9.9          1.8              None     None  ...           0.002                 0.354             4.9      0.012                None                   0.060         0.277
  4     TCB        4  2020             9.0          1.5              None     None  ...           0.003                 0.372             4.9      0.013                None                   0.057         0.202
  ```
</details>

## 2.7. Stock comparison
### 2.7.1. 🏭 Industry Analysis
```python
industry_analysis("VNM")
```

<details>
  <summary>Output</summary>

![preview](./src/stock_comparison_industries.png?raw=true)

```
>>> industry_analysis("VNM")
   ticker  marcap   price  numberOfDays  priceToEarning   peg  priceToBook  valueBeforeEbitda  dividend  ...  debtOnEbitda  income5year  sale5year income1quarter sale1quarter nextIncome  nextSale   rsi    rs
0     VNM  164897   78900             1            15.7  -3.1          5.0               12.6     0.037  ...           0.6        0.024      0.054         -0.249       -0.023       None      None  34.9  18.0
0     MSN  186524  158000            -1            21.8   0.0          5.7               22.5     0.008  ...           5.5        0.251      0.154          4.610        0.009        NaN       NaN  54.5  58.0
1     MCH   80250  112100             1            14.7   0.7          4.9               12.0     0.000  ...           1.2        0.152      0.150          0.381        0.372        NaN       NaN  48.6  36.0
2     MML   26061   79700            -1            19.6   0.0          4.7               24.9     0.000  ...           4.2       -0.029     -0.050          6.771       -0.243      0.904      0.22  58.8  60.0
```
</details>

### 2.7.2. 🔬 Stocks List Analysis
```python
stock_ls_analysis("TCB, BID, CEO, GMD")
```

<details>
  <summary>Output</summary>

![preview](./src/stock_ls_comparison.png)

```
  ticker  marcap  price  numberOfDays  priceToEarning  peg  priceToBook  valueBeforeEbitda  dividend  ...  debtOnEbitda  income5year  sale5year income1quarter  sale1quarter  nextIncome  nextSale   rsi    rs
0    GMD   15220  50500            -3            25.2  0.4          2.4               16.2       0.0  ...           1.8        0.092     -0.030          0.500         0.425         NaN       NaN  60.3  50.0
1    CEO   17062  66300             1           183.2 -0.8          5.7               81.8       0.0  ...           7.8       -0.099     -0.086            NaN         3.002      -1.469      -0.2  51.9  82.0
2    BID  225357  44550            -3            21.3  0.4          2.6                NaN       0.0  ...           NaN        0.115      0.154          0.083         0.000         NaN       NaN  49.1  34.0
3    TCB  178003  50700             1             9.9  0.2          1.9                NaN       0.0  ...           NaN        0.418      0.255          0.059         0.157         NaN       NaN  45.2  28.0
```

</details>

### 2.7.3. 🏢 Company Overview
```python
financial_report (symbol='SSI', report_type='BalanceSheet', frequency='Quarterly')
```

<details>
  <summary>Output</summary>

```
>>> company_overview('TCB')
  exchange    shortName  industryID industryIDv2  ... deltaInYear outstandingShare issueShare  ticker
0     HOSE  Techcombank         289         8355  ...      -0.075           3510.9     3510.9     TCB
```
</details>

### 2.7.4. 💵 Income Statement, Balance Sheet & Cashflow report

#### 2.7.4.1. Report from SSI
```python
financial_report (symbol='SSI', report_type='BalanceSheet', frequency='Quarterly)
```
- _report_type:_ You can choose 1 of 3 reports: `BalanceSheet`, `IncomeStatement`, or `CashFlow`
- _frequency:_ `Yearly` or `Quarterly`

<details>
  <summary>Output</summary>

  ```
                                        CHỈ TIÊU          2012          2013  ...          2019          2020          2021
  0                            TỔNG CỘNG TÀI SẢN  7.980876e+12  7.705074e+12  ...  2.704412e+13  3.576953e+13  5.079306e+13
  1                             TÀI SẢN NGẮN HẠN  4.837002e+12  4.467396e+12  ...  2.229087e+13  2.904003e+13  4.653960e+13
  3                    Tiền và tương đương tiền   1.947090e+12  1.838619e+12  ...  1.040783e+12  3.632519e+11  1.114235e+12
  4                                         Tiền  8.068605e+11  1.437619e+12  ...  2.606318e+11  2.319712e+11  4.741978e+11
  5                   Các khoản tương đương tiền  1.140230e+12  4.010000e+11  ...  7.801508e+11  1.312807e+11  6.400373e+11
  ..                                         ...           ...           ...  ...           ...           ...           ...
  149                   Lợi nhuận chưa phân phối  1.127003e+12  1.118080e+12  ...  2.941467e+12  2.676816e+12  2.927813e+12
  153         Vốn Ngân sách nhà nước và quỹ khác  0.000000e+00  0.000000e+00  ...  0.000000e+00  0.000000e+00  0.000000e+00
  154    Quỹ khen thưởng , phúc lợi (trước 2010)  0.000000e+00  0.000000e+00  ...  0.000000e+00  0.000000e+00  0.000000e+00
  157  LỢI ÍCH CỦA CỔ ĐÔNG THIỂU SỐ (trước 2015)  8.369917e+10  8.299030e+10  ...  0.000000e+00  0.000000e+00  0.000000e+00
  158                        TỔNG CỘNG NGUỒN VỐN  7.980876e+12  7.705074e+12  ...  2.704412e+13  3.576953e+13  5.079306e+13
  ```
</details>

#### 2.7.4.2. Report from TCBS

##### 📄 Income Statement

![income_statement](./src/financial_income_statement.png)
```python
financial_flow(symbol="TCB", report_type='incomestatement', report_range='quarterly')
```


<details>
  <summary>Output</summary>

```
        ticker  revenue  yearRevenueGrowth  quarterRevenueGrowth costOfGoodSold grossProfit  ...  investProfit  serviceProfit  otherProfit  provisionExpense operationIncome  ebitda
index                                                                                        ...
2021-Q4    TCB     7245              0.328                 0.074           None        None  ...           279           2103          532              -627            6767    None
2021-Q3    TCB     6742              0.310                 0.023           None        None  ...           384           1497          156              -589            6151    None
2021-Q2    TCB     6588              0.674                 0.076           None        None  ...           717           1457          444              -598            6615    None
2021-Q1    TCB     6124              0.454                 0.122           None        None  ...           812           1325          671              -851            6369    None
```
</details>

##### 🧾Balance Sheet

![balance_sheet](./src/financial_balancesheet.png)
```python
financial_flow(symbol="TCB", report_type='balancesheet', report_range='quarterly')
```

<details>
  <summary>Output</summary>

```
        ticker shortAsset  cash shortInvest shortReceivable inventory longAsset  fixedAsset  ...  payableInterest  receivableInterest deposit otherDebt  fund  unDistributedIncome  minorShareHolderProfit  payable
index                                                                                        ...

2021-Q4    TCB       None  3579        None            None      None      None        7224  ...             3098                5808  314753     33680  9156                47469                     845   475756
2021-Q3    TCB       None  3303        None            None      None      None        7106  ...             3074                6224  316376     34003  6784                45261                     753   453251
2021-Q2    TCB       None  3554        None            None      None      None        6739  ...             2643                5736  289335     27678  6790                40924                     659   420403
2021-Q1    TCB       None  4273        None            None      None      None        4726  ...             2897                5664  287446     26035  6790                36213                     563   3837
```
</details>

##### 💶Cashflow Report

```python
financial_flow(symbol="TCB", report_type='cashflow', report_range='quarterly')
```

<details>
  <summary>Output</summary>

```
        ticker  investCost  fromInvest  fromFinancial  fromSale  freeCashFlow
index
2021-Q4    TCB        -280        -276              0     -9328             0
2021-Q3    TCB        -180        -179             60     17974             0
2021-Q2    TCB        -337        -282              0     11205             0
2021-Q1    TCB        -143        -143              0     -6954             0
```
</details>

## 2.8. 🧧 Dividend Historical Data

```python
dividend_history("VNM")
```

<details>
  <summary>Output</summary>

```
   exerciseDate  cashYear  cashDividendPercentage issueMethod
0      10/01/22      2021                    0.14        cash
1      07/09/21      2021                    0.15        cash
2      07/06/21      2020                    0.11        cash
3      05/01/21      2020                    0.10        cash
```
</details>

## 2.9. ⭐General Rating

```python
general_rating("VNM")
```

<details>
  <summary>Output</summary>

```
   stockRating  valuation  financialHealth  businessModel  businessOperation  rsRating  taScore  ... ticker highestPrice  lowestPrice  priceChange3m  priceChange1y  beta   alpha
0          2.4        1.5              4.8            3.0                3.2       1.0      1.0  ...    VNM     102722.2      78600.0         -0.092         -0.232  0.49 -0.0014
```
</details>

## 2.10. 🌱 Business Model Rating
```python
biz_model_rating("VNM")
```

<details>
  <summary>Output</summary>

```
  ticker  businessModel  businessEfficiency  assetQuality  cashFlowQuality  bom  businessAdministration  productService  businessAdvantage  companyPosition  industry  operationRisk
0    VNM            3.0                   3             3                3    3                       3               3                  3                3         3              3
```
</details>

## 2.11. 🎮 Business Operation Rating
```python
biz_operation_rating("VNM")
```

<details>
  <summary>Output</summary>

```
      industryEn loanGrowth depositGrowth netInterestIncomeGrowth netInterestMargin  ... last5yearsFCFFGrowth lastYearGrossProfitMargin lastYearOperatingProfitMargin  lastYearNetProfitMargin  TOIGrowth
0  Food Products       None          None                    None              None  ...                    2                         5                             3                        4       None
```
</details>

## 2.12. 📑 Financial Health Rating
```python
financial_health_rating("VNM")
```

<details>
  <summary>Output</summary>

```
      industryEn loanDeposit badLoanGrossLoan badLoanAsset provisionBadLoan ticker  financialHealth  netDebtEquity  currentRatio  quickRatio  interestCoverage  netDebtEBITDA
0  Food Products        None             None         None             None    VNM              4.8              4             5           5                 5              5
```
</details>

## 2.13. 💲 Valuation Rating
```python
valuation_rating("VNM")
```

<details>
  <summary>Output</summary>

```
      industryEn ticker  valuation  pe  pb  ps  evebitda  dividendRate
0  Food Products    VNM        1.5   2   1   1         1             3
```
</details>

## 2.14.  💳 Industry Financial Health
```python
industry_financial_health("VNM")
```

<details>
  <summary>Output</summary>

```
  industryEn loanDeposit badLoanGrossLoan badLoanAsset provisionBadLoan ticker  financialHealth  netDebtEquity  currentRatio  quickRatio  interestCoverage  netDebtEBITDA
0       None        None             None         None             None    VNM              3.4              4             4           3                 3              3
```
</details>

## 2.15. 🌏 Market Watch
### 2.15.1. Top stocks

<details>
  <summary>SSI Top Stocks</summary>

Top Breakout > Top Gainers > Top Losers > Top Value > Top Volume
![top_mover](./src/ssi_top_breakout_gainer_loser.png)

Top New High > Top Foreign Trading > Top New Low
![top_foreigntrading_high_low](./src/top_foreigntrading_newhigh_newlow.png)

</details>

Input one of these following names to get your report: Breakout, Gainers, Losers, Value, Volume, ForeignTrading, NewLow, NewHigh
```python
market_top_mover('ForeignTrading')
```

<details>
  <summary>Output</summary>

```
    foreignBuyVolume  foreignBuyValue  ...                                          financial                                          technical
0          3826600.0     1.703888e+11  ...  {'organCode': 'DXG', 'rtd7': 14713.265320738, ...  {'organCode': 'DXG', 'sma20Past4': 34887.5, 's...
1          3270200.0     1.088892e+11  ...  {'organCode': 'STB', 'rtd7': 18173.6958318461,...  {'organCode': 'STB', 'sma20Past4': 34332.5, 's...
2          1456800.0     4.199166e+10  ...  {'organCode': 'FUEVFVND', 'rtd7': None, 'rtd11...  {'organCode': 'FUEVFVND', 'sma20Past4': 27993....
3          1033300.0     1.281170e+10  ...  {'organCode': 'FLC', 'rtd7': 12898.0038031343,...  {'organCode': 'FLC', 'sma20Past4': 12062.5, 's...
4           998600.0     5.324337e+10  ...  {'organCode': 'NLG', 'rtd7': 23318.1252311207,...  {'organCode': 'NLG', 'sma20Past4': 52385.0, 's...
```
</details>

### 2.15.2. Foreign Trade Insights
```python
fr_trade_heatmap ('All', 'FrBuyVol')
```
<details>
  <summary>Output</summary>

```
   organCode  name      value  percentPriceChange  ...  ceilingPrice  floorPrice        industry_name      rate
0        PVD   PVD  1433300.0            0.068627  ...       16350.0     14250.0              Dầu khí  0.040308
1        PVS   PVS   370100.0            0.096154  ...       22800.0     18800.0              Dầu khí  0.040308
2      PETRO   PLX   249700.0            0.014516  ...       33150.0     28850.0              Dầu khí  0.040308
3   PETECHIM   PTV     4000.0            0.064000  ...        5400.0      4000.0              Dầu khí  0.040308
4       BSRC   BSR     3800.0            0.002000  ...       17200.0     12800.0              Dầu khí  0.040308
..       ...   ...        ...                 ...  ...           ...         ...                  ...       ...
10      None  Khác   210200.0            0.027762  ...           0.0         0.0            Ngân hàng  0.050653
0        CMG   CMG    74400.0            0.024390  ...       43850.0     38150.0  Công nghệ Thông tin  0.034816
1        SAM   SAM    35700.0            0.020833  ...        7700.0      6700.0  Công nghệ Thông tin  0.034816
2        ELC   ELC     4100.0            0.049197  ...       10650.0      9270.0  Công nghệ Thông tin  0.034816
3        ITD   ITD     2000.0            0.068548  ...       13250.0     11550.0  Công nghệ Thông tin  0.034816

[92 rows x 10 columns]
```
</details>

# III. 🙋‍♂️ Contact Information

You can contact me at one of my social network profiles:

<div id="badges" align="center">
  <a href="https://www.linkedin.com/in/thinh-vu">
    <img src="https://img.shields.io/badge/LinkedIn-blue?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn Badge"/>
  </a>
  <a href="https://www.messenger.com/t/mr.thinh.ueh">
    <img src="https://img.shields.io/badge/Messenger-00B2FF?style=for-the-badge&logo=messenger&logoColor=white" alt="Messenger Badge"/>
  <a href="https://www.youtube.com/channel/UCYgG-bmk92OhYsP20TS0MbQ">
    <img src="https://img.shields.io/badge/YouTube-red?style=for-the-badge&logo=youtube&logoColor=white" alt="Youtube Badge"/>
  </a>
  </a>
    <a href="https://github.com/thinh-vu">
    <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="Github Badge"/>
  </a>
</div>

---

If you want to support my open-source projects, you can "buy me a coffee" via [Patreon](https://patreon.com/thinhvu?utm_medium=clipboard_copy&utm_source=copyLink&utm_campaign=creatorshare_creator) or Momo e-wallet (VN). Your support will help to maintain my blog hosting fee & to develop high-quality content.

![momo-qr](./src/momo-qr-thinhvu.jpeg)

# IV. ⚠ Disclaimer

This Python package has been made for **research purposes** to fit the needs that tcbs.com does not cover, 
so this package works like an Application Programming Interface (API) of tcbs.com developed in an **altruistic way**.

Conclude that **vnstock is not affiliated in any way to tcbs.com or ssi.com.vn or any dependant company**.

## V. Licensing

```
Copyright (c) 2022 Thinh Vu | thinh-vu @ Github | MIT

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```


