<h2 align="center">Vietnam Stock Market data extraction from TCBS with Python</h2>

vnstock is a Python package to retrieve the Vietnam stock market data from [TCBS](https://tcbs.com.vn).

vnstock allows the user to download historical, intraday stock data and market insights from [TCBS](https://tcbs.com.vn).

vnstock is relying on public/private APIs to provide stock data. It is **FREE** and has **NO LIMITATIONS**.


## 🛠 Installation

To get this package working, you will need to **install it via pip** (with a Python 3.7 version or higher) on the terminal by typing:

``$ pip install vnstock``

---

## 💻 Usage
You can understand some basic functionality of the vnstock package by following this guide.

### :chart_with_upwards_trend: Historical Data Retrieval

vnstock allows the user to **download stock historical data from TCBS**. In 
the example presented below, the historical data from the past years of a stock is retrieved. 

```python
from vnstock import *
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

```{r, engine='python', count_lines}
        open     high      low    close   volume tradingDate
0    32182.0  33157.0  31987.0  32279.0  4226500  2021-01-04
1    32279.0  33596.0  31938.0  32962.0  4851900  2021-01-05
2    33352.0  33352.0  32279.0  32572.0  3641300  2021-01-06
3    32864.0  33644.0  31694.0  33157.0  5753700  2021-01-07
4    33547.0  33937.0  32669.0  33059.0  4587500  2021-01-08
```

### 🔥 Intraday Trading Data
![intraday](./src/tcbs_intraday_screen1.png)
![intraday](./src/tcbs_intraday_screen2.png)

vnstock allows the user to **download intraday real-time/historical data**. In 
the example presented below, you can see the intraday historical data from the last weekday of the current week.

```python
from vnstock import *
df =  stock_intraday_data(symbol='GMD', 
                            page_num=0, 
                            page_size=5000))
print(df.head())
```

```{r, engine='python', count_lines}
p     volume       cp       rcp   a   ba   sa     hl  pcp      time
0     50700.0  169700  0.0  0.0      0.0  0.0   True  0.0  14:45:08
1     50800.0    1000  0.0  0.0  BU  0.0  0.0  False  0.0  14:30:05
2     50800.0     500  0.0  0.0  BU  0.0  0.0  False  0.0  14:30:05
3     50800.0   20000  0.0  0.0  BU  0.0  0.0   True  0.0  14:29:54
4     50700.0     300  0.0  0.0  SD  0.0  0.0  False  0.0  14:29:53
```
### 💰Financial Ratio

```python
from vnstock import *
financial_ratio("TCB")
```
Output:
```
 ticker  quarter  year  priceToEarning  priceToBook valueBeforeEbitda dividend  ...  badDebtOnAsset  liquidityOnLiability payableOnEquity cancelDebt ebitdaOnStockChange bookValuePerShareChange  creditGrowth
0     TCB        4  2021             9.9          1.9              None     None  ...           0.004                 0.382             5.1      0.004                None                   0.053         0.252
1     TCB        3  2021            10.0          2.0              None     None  ...           0.003                 0.405             5.1      0.004                None                   0.053         0.392
2     TCB        2  2021            11.4          2.2              None     None  ...           0.002                 0.370             5.0      0.008                None                   0.061         0.353
3     TCB        1  2021             9.9          1.8              None     None  ...           0.002                 0.354             4.9      0.012                None                   0.060         0.277
4     TCB        4  2020             9.0          1.5              None     None  ...           0.003                 0.372             4.9      0.013                None                   0.057         0.202
```

### 💵 Income Statement, Balance Sheet & Cashflow report

#### 📄 Income Statement
```python
from vnstock import *
financial_flow(symbol="TCB", report_type='incomestatement', report_range='quarterly')
```
Output:

```
        ticker  revenue  yearRevenueGrowth  quarterRevenueGrowth costOfGoodSold grossProfit  ...  investProfit  serviceProfit  otherProfit  provisionExpense operationIncome  ebitda
index                                                                                        ...
2021-Q4    TCB     7245              0.328                 0.074           None        None  ...           279           2103          532              -627            6767    None
2021-Q3    TCB     6742              0.310                 0.023           None        None  ...           384           1497          156              -589            6151    None
2021-Q2    TCB     6588              0.674                 0.076           None        None  ...           717           1457          444              -598            6615    None
2021-Q1    TCB     6124              0.454                 0.122           None        None  ...           812           1325          671              -851            6369    None
```

#### 🧾Balance Sheet
```python
from vnstock import *
financial_flow(symbol="TCB", report_type='balancesheet', report_range='quarterly')
```

Output:
```
        ticker shortAsset  cash shortInvest shortReceivable inventory longAsset  fixedAsset  ...  payableInterest  receivableInterest deposit otherDebt  fund  unDistributedIncome  minorShareHolderProfit  payable
index                                                                                        ...

2021-Q4    TCB       None  3579        None            None      None      None        7224  ...             3098                5808  314753     33680  9156                47469                     845   475756
2021-Q3    TCB       None  3303        None            None      None      None        7106  ...             3074                6224  316376     34003  6784                45261                     753   453251
2021-Q2    TCB       None  3554        None            None      None      None        6739  ...             2643                5736  289335     27678  6790                40924                     659   420403
2021-Q1    TCB       None  4273        None            None      None      None        4726  ...             2897                5664  287446     26035  6790                36213                     563   3837
```

#### 💶Cashflow Report

```python
from vnstock import *
financial_flow(symbol="TCB", report_type='cashflow', report_range='quarterly')
```
Output:
```
        ticker  investCost  fromInvest  fromFinancial  fromSale  freeCashFlow
index
2021-Q4    TCB        -280        -276              0     -9328             0
2021-Q3    TCB        -180        -179             60     17974             0
2021-Q2    TCB        -337        -282              0     11205             0
2021-Q1    TCB        -143        -143              0     -6954             0
```

### 🧧 Dividend Historical Data

```python
from vnstock import *
divident_history("VNM")
```

Output:
```
   exerciseDate  cashYear  cashDividendPercentage issueMethod
0      10/01/22      2021                    0.14        cash
1      07/09/21      2021                    0.15        cash
2      07/06/21      2020                    0.11        cash
3      05/01/21      2020                    0.10        cash
```

### ⭐General Rating

```python
from vnstock import *
general_rating("VNM")
```

Output:
```
   stockRating  valuation  financialHealth  businessModel  businessOperation  rsRating  taScore  ... ticker highestPrice  lowestPrice  priceChange3m  priceChange1y  beta   alpha
0          2.4        1.5              4.8            3.0                3.2       1.0      1.0  ...    VNM     102722.2      78600.0         -0.092         -0.232  0.49 -0.0014
```

### 🌱 Business Model Rating
```python
from vnstock import *
biz_model_rating("VNM")
```

Output:
```
  ticker  businessModel  businessEfficiency  assetQuality  cashFlowQuality  bom  businessAdministration  productService  businessAdvantage  companyPosition  industry  operationRisk
0    VNM            3.0                   3             3                3    3                       3               3                  3                3         3              3
```

### 🎮 Business Operation Rating
```python
from vnstock import *
biz_operation_rating("VNM")
```

Output:
```
      industryEn loanGrowth depositGrowth netInterestIncomeGrowth netInterestMargin  ... last5yearsFCFFGrowth lastYearGrossProfitMargin lastYearOperatingProfitMargin  lastYearNetProfitMargin  TOIGrowth
0  Food Products       None          None                    None              None  ...                    2                         5                             3                        4       None
```

### 📑 Financial Health Rating
```python
from vnstock import *
financial_health_rating("VNM")
```

Output:
```
      industryEn loanDeposit badLoanGrossLoan badLoanAsset provisionBadLoan ticker  financialHealth  netDebtEquity  currentRatio  quickRatio  interestCoverage  netDebtEBITDA
0  Food Products        None             None         None             None    VNM              4.8              4             5           5                 5              5
```

### 💲 Valuation Rating
```python
from vnstock import *
valuation_rating("VNM")
```

Output:
```
      industryEn ticker  valuation  pe  pb  ps  evebitda  dividendRate
0  Food Products    VNM        1.5   2   1   1         1             3
```

### 💳 Industry Financial Health
```python
from vnstock import *
industry_financial_health("VNM")
```

Output:
```
  industryEn loanDeposit badLoanGrossLoan badLoanAsset provisionBadLoan ticker  financialHealth  netDebtEquity  currentRatio  quickRatio  interestCoverage  netDebtEBITDA
0       None        None             None         None             None    VNM              3.4              4             4           3                 3              3
```

### 🏭 Industry Analysis
```python
from vnstock import *
industry_analysis("VNM")
```

Output:
```
>>> industry_analysis("VNM")
   ticker  marcap   price  numberOfDays  priceToEarning   peg  priceToBook  valueBeforeEbitda  dividend  ...  debtOnEbitda  income5year  sale5year income1quarter sale1quarter nextIncome  nextSale   rsi    rs
0     MSN  186524  158000            -1            21.8   0.0          5.7               22.5     0.008  ...           5.5        0.251      0.154          4.610        0.009        NaN       NaN  54.5  58.0
1     MCH   80250  112100             1            14.7   0.7          4.9               12.0     0.000  ...           1.2        0.152      0.150          0.381        0.372        NaN       NaN  48.6  36.0
2     MML   26061   79700            -1            19.6   0.0          4.7               24.9     0.000  ...           4.2       -0.029     -0.050          6.771       -0.243      0.904      0.22  58.8  60.0
3     QNS   16340   45800            -2            13.2   0.7          2.3                9.9     0.000  ...           1.1       -0.025      0.010          0.070       -0.263      0.106      0.10  34.8  18.0
4     SBT   14902   22900             1            19.2   0.6          1.7               14.3     0.000  ...           5.9        0.210      0.308          0.101        0.157        NaN       NaN  48.6  42.0
```

## 🙋‍♂️ Contact Information

You can contact me at one of my social network profiles:

- :briefcase: LinkedIn: https://linkedin.com/in/thinh-vu
- :octocat: GitHub: https://github.com/thinh-vu

---

## ⚠ Disclaimer

This Python package has been made for **research purposes** to fit the needs that tcbs.com does not cover, 
so this package works like an Application Programming Interface (API) of tcbs.com developed in an **altruistic way**.

Conclude that **vnstock is not affiliated in any way to tcbs.com or any dependant company**.


