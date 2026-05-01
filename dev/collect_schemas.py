import pandas as pd
from vnstock import Market, Reference, Fundamental
import json
import os

def get_schema(df):
    if not isinstance(df, pd.DataFrame):
        return str(type(df))
    return {
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "sample": df.head(2).to_dict(orient='records')
    }

results = {}

print("Fetching Market Equity History...")
try:
    df = Market().equity('SSI').history()
    results["Market.equity.history"] = get_schema(df)
except Exception as e:
    results["Market.equity.history"] = str(e)

print("Fetching Market Equity Intraday...")
try:
    df = Market().equity('SSI').intraday()
    results["Market.equity.intraday"] = get_schema(df)
except Exception as e:
    results["Market.equity.intraday"] = str(e)

print("Fetching Reference Listing Symbols...")
try:
    df = Reference().listing.symbols_by_exchange()
    results["Reference.listing.symbols_by_exchange"] = get_schema(df)
except Exception as e:
    results["Reference.listing.symbols_by_exchange"] = str(e)

print("Fetching Fundamental Equity Financial Report...")
try:
    df = Fundamental().equity('SSI').financial_report(report_type='income_statement', period='quarter')
    results["Fundamental.equity.financial_report"] = get_schema(df)
except Exception as e:
    results["Fundamental.equity.financial_report"] = str(e)

print("Fetching Fundamental Equity Ratio...")
try:
    df = Fundamental().equity('SSI').ratio()
    results["Fundamental.equity.ratio"] = get_schema(df)
except Exception as e:
    results["Fundamental.equity.ratio"] = str(e)

# Save to JSON for later use
os.makedirs('dev/schemas', exist_ok=True)
with open('dev/schemas/raw_snapshot.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Schema collection complete. Saved to dev/schemas/raw_snapshot.json")
