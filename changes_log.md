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
> The `main` branch is for major updates only, while the `beta` branch is for minor updates. Pypi package will be reflected the `main` branch from now on.

- The listing_companies() function can now read the company listing from either a csv file on this github repo or a live API request.
- The stock_intraday_data () function has a new limit of 100 for the page_size parameter imposed by the TCBS.
- The README.md file reflects the changes made to the above functions.pip