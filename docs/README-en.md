<h2 align="center">Vietnam Stock Market data loader using Python</h2>

---
<div id="badges" align="center">
<img src="https://img.shields.io/pypi/pyversions/vnstock?logoColor=brown&style=plastic" alt= "Version"/>
<img src="https://img.shields.io/pypi/dm/vnstock" alt="Download Badge"/>
<img src="https://img.shields.io/github/last-commit/thinh-vu/vnstock" alt="Commit Badge"/>
<img src="https://img.shields.io/github/license/thinh-vu/vnstock?color=red" alt="License Badge"/>
</div>

---

🌐 View in **[Vietnamese](https://github.com/thinh-vu/vnstock/blob/main/README.md)**

TABLE OF CONTENTS

- [I. 🎤 Introduction](#i--introduction)
- [II. 📚 User Guide for Beginners](#ii--user-guide-for-beginners)
- [III. 💻 Usage](#iii--usage)
- [IV. 🙋‍♂️ Contact Information](#iv-️-contact-information)
- [V. 💪 Join Us in Supporting vnstock](#v--join-us-in-supporting-vnstock)
- [VI. ⚖ Disclaimer](#vi--disclaimer)
- [VII. Licensing](#vii-licensing)


# I. 🎤 Introduction
## 1.1. General Introduction
vnstock is a Python library designed to easily and freely download Vietnamese stock market data. vnstock utilizes reliable data sources, including but not limited to securities companies and market analysis firms in Vietnam. The library is built based on the principles of simplicity and open-source, with most functions written using the request and pandas libraries available in the Google Colab environment. Therefore, users do not need to install additional libraries.

## 1.2. Key Features
vnstock provides a variety of features, such as downloading historical price data, listed company information, and market information for all listed securities.

## 1.3. Data Sources
This Python library connects to public APIs of data providers to download data and work with them as DataFrames in Python projects. Accessing this data is completely **FREE**.

## 1.4. Tips
- Stay updated on vnstock changes using the `Watch` feature. Currently, vnstock is regularly updated on a weekly basis through the `beta` branch, so following this repository will help you stay up to date with the latest changes.
- Show your support for the `vnstock` repository by starring it. This also helps vnstock reach a wider audience of interested users.

<details>
  <summary> Minh họa tính năng Watch và Star </summary>

  ![watch-star](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images/vnstock-watch-and-star.png?raw=true)

</details>


## 1.5. Contributing to the vnstock Open Source Project
You can contribute to the development of vnstock through various means, including building and improving the source code or translating project documentation. To get started, you can fork this repository to your account, make modifications to the source code, and create a pull request to request source code updates. After reviewing and approving the changes, the contributed source code will be merged into vnstock.

# II. 📚 User Guide for Beginners
## 2.1. Important Resources

### 2.1.2 Blog

👉 For more information and illustrations on how to use, please visit the blog post, available in Vietnamese/English [here](https://thinhvu.com/2022/09/22/vnstock-api-tai-du-lieu-chung-khoan-python?utm_source=github&utm_medium=vnstock).

### 2.1.2 Notebook Illustration
👉 You can open the Jupyter Notebook file [vnstock_demo_index_all_functions_testing](https://github.com/thinh-vu/vnstock/blob/beta/demo/gen2_vnstock_demo_index_all_functions_testing_2023_07_07.ipynb) to try out all the functions of vnstock. To use, click the ![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg) button at the top of the notebook to open it with Google Colab.

### 2.1.3. Docstring
All functions of vnstock are provided with complete docstrings, while this README.md file may not include a full description of the parameters allowed for each function. You can refer to the code hints when writing commands in IDEs like Google Colab, Visual Studio Code, or Jupyter Notebook, or open the source code on Github for more details. In the future, vnstock will provide full descriptions in the README.md when possible.

<details>
  <summary>Docstring in Google Colab</summary>
  Syntax hints for functions are displayed when writing any function belonging to vnstock. In this example, it is shown in the Google Colab interface.

  ![docstring_ide](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images/docstring_suggestion.jpeg?raw=true)

</details>

<details>
  <summary>Docstring in source code</summary>
  
  Open the source code file [vnstock.py](https://github.com/thinh-vu/vnstock/blob/beta/vnstock/stock.py) and find the function you want to look up the docstring for.

  ![docstring_source](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images/docstring_source_code.png?raw=true)

</details>

### 2.1.4. Building the vnstock Community

🖐 If you find this library valuable and would like to support the author in maintaining vnstock as open-source and free, you can contribute to the development of this project. For more details, please refer to the blog post: [Building a Strong VNStock Community Together](https://thinhvu.com/2023/04/15/xay-dung-cong-dong-vnstock-vung-manh/).

<details>
  <summary>Supporting the vnstock Development Fund</summary>
  If vnstock has been helpful to you, you can contribute to the development fund of this application through either bank transfer or Momo. All contributions are greatly appreciated and serve as motivation for the author to maintain vnstock as a useful, free, and accessible resource for the community.

  - ![vcb-qr](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images/vcb-qr-thinhvu.jpg?raw=true)
  - ![momo-qr](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images/momo-qr-thinhvu.jpeg?raw=true)

</details>

### 2.1.5. Development Roadmap

🔥 You can refer to [Ideas for Advanced Features in upcoming versions](https://github.com/users/thinh-vu/projects/1/views/4) to accompany vnstock on its journey.

### 2.1.6. Notes

👉 Starting from version 0.1.3, all updates regarding features and enhancements for the library are compiled in the [Changelog](https://github.com/thinh-vu/vnstock/blob/beta/changes_log.md) file.

## 2.2 🛠 Installing vnstock
### Step 1. Choose the appropriate version

> vnstock is developed in two separate branches. You need to choose the appropriate version and *copy the corresponding command to perform the installation in the next step*:

- `stable` version (stable development) is shared through pypi.org and the `main` branch on this Github repository. To install the stable version, use the following simple command: 
`pip install vnstock` or install directly from Github with the command:

  `pip install git+https://github.com/thinh-vu/vnstock.git@main`

- `beta` version (receives the latest updates) is shared in the `beta` branch of the Github repository.

  `pip install git+https://github.com/thinh-vu/vnstock.git@beta`

<details>
  <summary> Choose the appropriate branch </summary>

  ![select_branch](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images/vnstock_select_branch.jpeg?raw=true)

</details>

### Step 2. Run the installation command

> When using the demo file [vnstock_demo_index_all_functions_testing_2023_06_22.ipynb](https://github.com/thinh-vu/vnstock/blob/beta/demo/gen2_vnstock_demo_index_all_functions_testing_2023_07_07.ipynb) to get started, the necessary installation commands are provided for you to execute (run).

**pip is used to install vnstock**. pip is available in most Python distributions. The minimum required Python version for vnstock is 3.7. You can paste the command you copied in Step 1 and run it in your Python environment.

- CLI: Open Terminal (macOS/Linux) or Command Prompt (Windows Desktop) and paste the command above, then press Enter to install.
---

# III. 💻 Usage
You can understand some basic functionality of the vnstock package by following this guide.
First of all, you need to import the vnstock package to your python project by running this code. After that, feel free to call any functions listed below.
```python
from vnstock import *
```

## 2.1 📰 All listing companies
```python
listing_companies()
```
This function reads data from the attached CSV file on Github by default (in the /data directory of this repository). Since the list of listed companies doesn't change frequently, this doesn't pose much of an obstacle. Currently, the mode to read data from APIs has been temporarily removed due to access restrictions imposed by the data providers."

<details>
  <summary>Output</summary>

```
  ticker comGroupCode                                       organName  ...  VNMAT VNREAL  VNUTI
0    VVS   UpcomIndex  Công ty Cổ phần Đầu tư Phát triển Máy Việt Nam  ...  False  False  False
1    XDC   UpcomIndex   Công ty TNHH MTV Xây dựng Công trình Tân Cảng  ...  False  False  False
2    HSV   UpcomIndex           Công ty Cổ phần Tập đoàn HSV Việt Nam  ...  False  False  False
```

</details>

## 2.2. Ticker overview
```python
company_overview('TCB')
```

<details>
  <summary>Output</summary>

  ```
  >>> company_overview('TCB')
    exchange    shortName  industryID industryIDv2   industry  ... deltaInMonth deltaInYear  outstandingShare  issueShare  ticker
  0     HOSE  Techcombank         289         8355  Ngân hàng  ...       -0.027      -0.038            3510.9      3510.9     TCB
  ```

</details>

## 2.3. 📈 Historical Data Retrieval

vnstock allows users to download historical stock trading data with 5 levels of detail based on time intervals: 1 minute, 15 minutes, 30 minutes, 1 hour, 1 day. In the example below, price data is retrieved at the daily resolution.

```python
df = stock_historical_data(symbol='GMD', 
                           start_date="2021-01-01", 
                           end_date='2022-02-25', 
                           resolution='1D')
print(df.head())
```
- New: 
  - The resolution parameter can accept the following values: 1D (default, 1 day), '1' (1 minute), 15 (15 minutes), 30 (30 minutes), '1H' (1 hour).
  - The `type = 'stock'` parameter allows retrieving price data for stock symbols. The `type = 'index'` parameter allows retrieving price data for index codes. Supported index codes include: VNINDEX, VN30, HNX, HNX30, UPCOM, VNXALLSHARE, VN30F1M, VN30F2M, VN30F1Q, VN30F2Q.

- You can also use a shorter function format as shown below, which applies to all functions as long as the parameters are entered in the correct order:

- Retrieve historical data of a stock code.
```python
df = stock_historical_data("GMD", "2021-01-01", "2022-02-25", "1D")
print(df.head())
```
The result should look like this:

<details>
  <summary>Output</summary>

  ```{r, engine='python', count_lines}
     time        open     high     low      close    volume
  0  2021-01-04  32182.0  33157.0  31987.0  32279.0  4226500
  1  2021-01-05  32279.0  33596.0  31938.0  32962.0  4851900
  2  2021-01-06  33352.0  33352.0  32279.0  32572.0  3641300
  ```
</details>

  - Retrieve historical data of an index code.
  ```python
  df = stock_historical_data("VNINDEX", "2021-01-01", "2022-02-25", "1D", 'index')
  print(df)
  ```

## 2.4. 📊 Price Table
You can download the price table of a selected list of stocks to facilitate analysis and algorithm setup, making it easier than directly viewing the stock prices on the stock brokage's website.

<details>
  <summary>Price Table</summary>

  ![price_board](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images//tcbs_trading_board_sector.png?raw=true)

</details>

### 3.4.1. Price Depth, Volume, and Matched Orders Information
```python
price_depth('TCB,SSI,VND')
```

Using this function allows you to analyze price depth and volume on the price table of one or a list of stock codes. You can combine this function with the price_board function to gather diverse information about price, volume, indices, and trading information to filter and track stocks according to your needs.

<details>
  <summary>Output</summary>
  >>> price_depth('TCB,SSI,VND')
  Mã CP  Giá tham chiếu  Giá Trần  Giá Sàn  Giá mua 3 KL mua 3  Giá mua 2 KL mua 2  Giá mua 1  ... KL bán 1  Giá bán 2  KL bán 2  Giá bán 3 KL bán 3  Tổng Khối Lượng ĐTNN Mua  ĐTNN Bán  ĐTNN Room
0   TCB           31950     34150    29750      31900       10      31850      130      31800  ...     9240      32000     19940      32049     7750           447200        0         0          0     
1   SSI           28400     30350    26450      28450      100      28400     9850      28350  ...    30640      28550     22730      28600    48410          1610280   142759     17353  803963854     
2   VND           17950     19200    16700      18450    11620      18400    38790      18350  ...    73180      18550     87830      18600   223700          4360710   152966      8355  932083910     

[3 rows x 22 columns]
</details>

## 2.5. 🔥 Intraday Trading Data

<details>
  <summary>Intraday view on TCBS</summary>

  ![intraday](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images//tcbs_intraday_screen1.png?raw=true)
  ![intraday](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images//tcbs_intraday_screen2.png?raw=true)

</details>
vnstock allows the user to **download intraday real-time/historical data**. In 
the example presented below, you can see the intraday historical data from the last weekday of the current week.

```python
df =  stock_intraday_data(symbol='TCB', 
                            page_size=500)
print(df)
```

<details>
  <summary>Terminal output</summary>

  ```{r, engine='python', count_lines}
>>> stock_intraday_data('TCB', 500)

  ticker      time  orderType investorType  volume  averagePrice  orderCount
0    TCB  14:29:55  Sell Down        SHEEP    1000       32700.0           1
1    TCB  14:29:47     Buy Up        SHEEP     200       32750.0           1
2    TCB  14:29:44  Sell Down         WOLF    8000       32700.0          14
3    TCB  14:29:41  Sell Down        SHEEP    1000       32700.0           5
4    TCB  14:29:36  Sell Down         WOLF   23800       32700.0          10
  ```

</details>

<details>
  <summary>Glossary</summary>
  
  - When a large order (from Sharks, big players, organizations, etc.) is actively placed for buying or selling on the Exchange, it typically gets matched with multiple small orders awaiting execution (buy or sell). If we only observe real-time individual matched orders, it becomes difficult to detect the entry of large orders (from Sharks, big players, etc.) that have just been pushed into the Exchange. Therefore, we "accumulate" these matched orders (resulting from a large active order being placed on the Exchange within a very short period) to help investors identify large orders (from Sharks, big players, etc.) more accurately. Shark orders are highlighted in green (for active buying) and red (for active selling).

  - Sharks (CM) refer to large investors, institutions, or market leaders who have a significant influence on the market. The value of an order is greater than 1 billion Vietnamese dong per order. The 1-minute chart reflects the last 60 minutes of data, the 1-week chart summarizes data every 15 minutes for one week, and the 1-month chart aggregates daily data for one month.

  - Wolves (SG) refer to experienced investors with relatively high-value orders. The value of an order ranges from 200 million to 1 billion Vietnamese dong per order.

  - Sheep (CN) refer to small retail investors with low-value transactions and low active buying or selling. The value of a Buy or Sell active order is less than 200 million Vietnamese dong per order.

  - Active buying (or Buy Up) occurs when an investor proactively places a buy order at the best ask price to match immediately. As a result, the matched price for this order typically pushes the price higher than the previous market price.

  - Active selling (or Sell Down) occurs when an investor proactively places a sell order below the current price (or market price) of the stock, matching it immediately with the best bid price. Consequently, the market price is pulled down lower than the previous market price. Analyzing the volume of Buy Up and Sell Down transactions helps evaluate the relationship between supply (Sell Down) and demand (Buy Up) in actual matched order transactions, providing a relative assessment of money flow trends. When the percentage of Buy Up transactions compared to the total of Buy Up and Sell Down transactions is greater than 50%, it indicates that the market is inclined towards more buying than selling, and vice versa. This helps determine the money flow in and out of each stock. When this percentage undergoes a sudden significant change (>70% or <30%) compared to the equilibrium point (50%), it signals market buying or selling regardless of other factors.

</details>

## 2.6. 💰Financial Ratio
### 2.6.1. Report from SSI

<details>
  <summary>Suspended due to data source from SSI is blocked</summary>

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

![preview](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images/stock_comparison_industries.png?raw=true)

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

![preview](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images/stock_ls_comparison.png?raw=true)

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
company_overview('TCB')
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

<details>
  <summary>Suspended due to data source from SSI is blocked</summary>

```python
financial_report (symbol='SSI', report_type='BalanceSheet', frequency='Quarterly')
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

</details>

#### 2.7.4.2. Report from TCBS

##### 📄 Income Statement

![income_statement](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images//financial_income_statement.png?raw=true)
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

![balance_sheet](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images//financial_balancesheet.png?raw=true)
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

##### 💶 Cashflow Report

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

<details>
  <summary>Suspended due to data source from SSI is blocked</summary>

### 2.15.1. Top stocks

<details>
  <summary>SSI Top Stocks</summary>

Top Breakout > Top Gainers > Top Losers > Top Value > Top Volume
![top_mover](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images/ssi_top_breakout_gainer_loser.png?raw=true)

Top New High > Top Foreign Trading > Top New Low
![top_foreigntrading_high_low](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images/top_foreigntrading_newhigh_newlow.png?raw=true)

</details>

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

### 2.15.3. Market latest indices & values
![latest_indices](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images//get_latest_indices.png?raw=true)

Retrieve the latest indices values & brief insights

```python
get_latest_indices()
```

<details>
  <summary>Output</summary>

  ```
  >>> get_latest_indices()
    indexId comGroupCode  indexValue          tradingDate  ...  matchValue  ceiling  floor  marketStatus
0         0      VNINDEX     1108.08  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
1         0         VN30     1121.92  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
2         0     HNXIndex      219.87  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
3         0        HNX30      378.94  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
4         0   UpcomIndex       73.98  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
5         0       VNXALL     1707.39  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
6         0        VN100     1063.59  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
7         0        VNALL     1066.54  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
8         0       VNCOND     1537.34  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
9         0       VNCONS      793.25  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
10        0    VNDIAMOND     1689.15  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
11        0        VNENE      541.51  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
12        0        VNFIN     1252.54  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
13        0    VNFINLEAD     1631.16  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
14        0  VNFINSELECT     1676.21  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
15        0       VNHEAL     1552.19  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
16        0        VNIND      628.34  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
17        0         VNIT     2631.82  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
18        0        VNMAT     1534.50  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
19        0        VNMID     1394.75  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
20        0       VNREAL      981.94  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
21        0         VNSI     1715.37  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
22        0        VNSML     1140.40  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
23        0        VNUTI      874.84  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
24        0        VNX50     1805.33  2023-01-19T00:00:00  ...         0.0      0.0    0.0          None
  ```
</details>

### 2.15.4. Market latest indices in depth data
![index_series_data](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images//get_index_series_data.png?raw=true)

```python
get_index_series(index_code='VNINDEX', time_range='OneYear')
```
- Data provider: FiinTrade on SSI iBoard
- Use one of the following index code:
  
  ```
  'VNINDEX', 'VN30', 'HNXIndex', 'HNX30', 'UpcomIndex', 'VNXALL',
  'VN100','VNALL', 'VNCOND', 'VNCONS','VNDIAMOND', 'VNENE', 'VNFIN',
  'VNFINLEAD', 'VNFINSELECT', 'VNHEAL', 'VNIND', 'VNIT', 'VNMAT', 'VNMID',
  'VNREAL', 'VNSI', 'VNSML', 'VNUTI', 'VNX50'
  ```
  You can get the complete list of the latest indices from `get_latest_indices()` function

- `time_range`: Use one of the following values:
 ```
 'OneDay', 'OneWeek', 'OneMonth', 'ThreeMonth', 'SixMonths', 'YearToDate', 'OneYear', 'ThreeYears', 'FiveYears'
 ```
<details>
  <summary>Output</summary>

  ```
  >>> get_index_series(index_code='VNINDEX', time_range='OneYear')
      comGroupCode  indexValue          tradingDate  ...    matchValue  totalMatchVolume  totalMatchValue
  0        VNINDEX     1470.76  2022-01-27T00:00:00  ...  1.554536e+13       498256400.0     1.554536e+13
  1        VNINDEX     1478.96  2022-01-28T00:00:00  ...  1.913215e+13       634887600.0     1.913215e+13
  2        VNINDEX     1497.66  2022-02-07T00:00:00  ...  1.710999e+13       516533800.0     1.710999e+13
  3        VNINDEX     1500.99  2022-02-08T00:00:00  ...  2.106676e+13       660158600.0     2.106676e+13
  4        VNINDEX     1505.38  2022-02-09T00:00:00  ...  2.360041e+13       722161500.0     2.360041e+13
  ..           ...         ...                  ...  ...           ...               ...              ...
  241      VNINDEX     1060.17  2023-01-13T00:00:00  ...  7.884840e+12       459494342.0     7.884840e+12
  242      VNINDEX     1066.68  2023-01-16T00:00:00  ...  6.724499e+12       391079501.0     6.724499e+12
  243      VNINDEX     1088.29  2023-01-17T00:00:00  ...  1.016031e+13       566247477.0     1.016031e+13
  244      VNINDEX     1098.28  2023-01-18T00:00:00  ...  9.377296e+12       531786150.0     9.377296e+12
  245      VNINDEX     1108.08  2023-01-19T00:00:00  ...  1.054607e+13       556193050.0     1.054607e+13

  [246 rows x 14 columns]
  ```
</details>

</details>

# IV. 🙋‍♂️ Contact Information

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

# V. 💪 Join Us in Supporting vnstock

If you find value in vnstock and my open-source projects, you can support their development by making a contribution or simply treating me to a cup of coffee as a token of appreciation.

You have three options to contribute: Momo, Bank Transfer, and Paypal. Your contribution will help me cover the hosting fees for my blog and continue creating high-quality content. Thank you for your support!

- [Paypal](https://paypal.me/thinhvuphoto?country.x=VN&locale.x=en_US)
- ![momo-qr](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images/momo-qr-thinhvu.jpeg)
- ![vcb-qr](https://github.com/thinh-vu/vnstock/blob/beta/docs/assets/images/vcb-qr-thinhvu.jpg)

# VI. ⚖ Disclaimer
vnstock is designed solely for the purpose of analysis and practical investment research. Any misuse or unauthorized use of the library for malicious purposes, such as attacking public APIs or causing harm to systems through denial of service or similar actions, is strictly beyond the intended scope of usage and falls outside the responsibility of the development team.

vnstock is developed with the purpose of providing simple and free research tools to facilitate easy access and analysis of stock market data. The availability and accuracy of the data depend on the data sources. Therefore, users are advised to exercise caution and discretion when utilizing the library.
<details>
  <summary>Read more</summary>

  In any circumstances, the user assumes full responsibility for the decision to use the data extracted from vnstock and bears complete liability for any resulting losses. It is strongly recommended to independently verify the accuracy and reliability of the data before making use of it.

  Engaging in stock market data usage and investment decisions entails risks and may lead to financial losses. Users are encouraged to seek guidance from financial experts and comply with securities regulations in Vietnam and internationally when participating in stock trading activities.

  Please note that vnstock does not assume responsibility and holds no legal liability for any losses or damages arising from the utilization of this software package.

</details>

# VII. Licensing

```
Copyright (c) 2022 Thinh Vu | thinh-vu @ Github | MIT

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
