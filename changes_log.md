# Updated 2023-09-05
- Restructured vnstock from a single module to multiple modules, with each module responsible for a set of functions, enhancing both readability and ease of maintenance.
- Expanded the package with the addition of 10 new functions, which include:
  - In the Fundamental Analysis category: company_profile, company_large_shareholders, company_fundamental_ratio, ticker_price_volatility,
company_insider_deals, company_subsidiaries_listing, company_officers, company_events, and company_news.
  - In the Financial Analysis category: stock_evaluation.
- Updated the demo file to incorporate the most recent enhancements.
- Revised and updated the README file.
- Introduced the official website for vnstock at vnstock.site and the vnstock web app.

# Updated 2023-08-22
- Updated the listing_companies data file to the latest version.
- Updated the `financial flow` function
  - Add `get_all` parameter to get all available data or only the latest data (5 years or 10 quarters).
- Update demo notebook to reflect the latest changes.

# Updated 2023-07-24
- Initiate the implementation of derivatives data retrieval functionality.
- Integrate a stock screening function into the library.
- Enhanced the stock_historical_data function with the following updates:
  - When the resolution is set to 1D, the time column will now be displayed in the YYYY-mm-dd date format.
  - Introduced a new value, derivative, for the type parameter, enabling the retrieval of derivatives data.
  - ~~ Added `ticker` column to the returned DataFrame.~~
- The function references in the README file have been restructured by use cases, such as Technical Analysis, Fundamental Analysis, Stock screening, etc. This will provide a more user-friendly and organized documentation for the python package. The English version of the README file has also been updated to match the Vietnamese version.

# Updated 2023-07-22
- Added a new example code to the existing [demo notebook](https://github.com/thinh-vu/vnstock/blob/beta/demo/gen2_vnstock_demo_index_all_functions_testing_2023.ipynb) that demonstrates how to export data from Google Colab to Google Sheets.

# Updated 2023-07-14
- Released version 0.17 on Pypi
- The `beta` branch has been promoted to become the default branch, while the `main` branch will now serve as the stable version repository.
- The changes made in the `beta` branch will be merged into the `main` branch and released on PyPI on a monthly basis, starting from now onwards
- The README.md file has been updated to synchronize the English and Vietnamese versions.
- The database file listing_companies_enhanced-2023.csv in the data folder of this repository has been updated for the listing_companies function.
- A new function, price_depth, has been introduced to retrieve trading prices and volume for a list of stocks. This function can be used in conjunction with the price_board function.

# Update 2023-07-13
- Classified vnstock functions in the demo Jupyter Notebook based on 5 main pillars:
  1. Market Watch
  2. Fundamental Analysis
  3. Technical Analysis
  4. Stock Pick
  5. Trading Center
- Revised function demos to include recently updated functions.
- Restore the unit price of stock_historical_data from 1000 VND to VND by multiplying it by 1000.
- The `price_board` function has been updated.
- Implemented additional functions in the `utils.py` module to extract date values in the format of YYYY-mm-dd.

# Updated 2023-07-05
- The README.md file has been revised (applied to the Vietnamese language first).
- Functions related to SSI data source that were unavailable have been removed.
- The `financial_ratio` function has been enhanced with the following updates:
  - The resulting DataFrame now has a transposed structure, with the year/quarter serving as the index, facilitating usability.
  - The `is_all` parameter has been made optional.
- The `industry_analysis` and stock_ls_analysis functions have been improved:
  - The resulting DataFrame now has a transposed structure, with the stock ticker names as column headers, making it more user-friendly.
  - An additional `lang` parameter has been introduced, allowing the display of DataFrame columns in Vietnamese/English labels.

# Updated 2023-06-29
- Updated the stock_intraday_data function to elaborate more insights the data returned by the function and make it usable.
- Updated the stock_historical_data to support getting indices historical data.

# Updated 2023-06-22
- Referred to as version 0.15 (coming soon on Pypi)
- Introduce a new feature to the stock_historical_data function, enabling retrieval of data with multiple time resolutions. The corresponding API endpoint supporting this function has been upgraded.
  - Include a resolution parameter to allow users to obtain price data at intervals of 1 minute, 15 minutes, 30 minutes, 1 hour, or 1 day.
  - Modify the column name in the returned dataframe from tradingDate to time.
- Clearly mark functions that are not available for SSI API endpoints.
- The `mode='live'` option in the function listing_companies() has been removed. The function will now only read the company listing from a csv file on this github repo.
- Update the repo folder tree, added data folder data files, demo folder to store demo files.

# Updated 2023-06-07
Assist in providing a Vietnamese translation for the README.md file, which will be beneficial for local users.

# Updated 2023-05-20
> The `main` branch is dedicated to major updates only, while the `beta` branch is used for minor updates. Starting from now, the PyPI package will reflect the contents of the `main` branch.

- The listing_companies() function can now read the company listing from either a csv file on this github repo or a live API request.
- The stock_intraday_data () function has a new limit of 100 for the page_size parameter imposed by the TCBS.