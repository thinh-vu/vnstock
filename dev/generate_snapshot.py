import datetime
import json
import os

import pandas as pd
import toml

from vnstock import Fundamental, Market, Reference

# Expanded Universe to ensure we find data for snapshots
# VN30 + High-activity stocks + Stocks with diverse data
VN30 = ["SSI", "VCB", "FPT", "VIC", "HPG", "VNM", "TCB", "MBB", "MWG", "VHM", "STB", "ACB", "BID", "CTG", "GVR", "HDB", "MSN", "PLX", "POW", "SAB", "SHB", "SSB", "TPB", "VIB", "VJC", "VPB", "VRE", "BCM"]
EXTENDED = ["HAG", "DXG", "NVL", "VND", "DIG", "PDR", "GEX", "KBC", "SHS", "VIX", "TCH", "L14", "CEO", "ITA", "HQC", "VOS", "PVT", "PVS", "PVD", "GAS", "POW", "NT2", "REE"]
FULL_UNIVERSE = list(dict.fromkeys(VN30 + EXTENDED)) # Unique list

def get_project_version():
    try:
        with open('pyproject.toml', 'r', encoding='utf-8') as f:
            data = toml.load(f)
            return data.get('project', {}).get('version', 'Unknown')
    except Exception:
        return 'Unknown'

def get_metadata(df, notation, module_path, ticker_used=None):
    if df is None:
        return None

    if isinstance(df, dict):
        return {
            "notation": notation,
            "module": module_path,
            "ticker_used": ticker_used,
            "columns": list(df.keys()),
            "dtypes": {k: type(v).__name__ for k, v in df.items()},
            "sample": [df]
        }

    if not isinstance(df, pd.DataFrame):
        return None

    if df.empty:
        return {
            "notation": notation,
            "module": module_path,
            "ticker_used": ticker_used,
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "sample": []
        }

    sample = df.head(3).to_dict(orient='records')
    for record in sample:
        for key, value in record.items():
            if isinstance(value, (pd.Timestamp, pd.Timedelta)):
                record[key] = value.isoformat() if hasattr(value, 'isoformat') else str(value)
            elif pd.isna(value):
                record[key] = None

    return {
        "notation": notation,
        "module": module_path,
        "ticker_used": ticker_used,
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "sample": sample
    }

def try_fetch_with_universe(func_factory):
    """
    Tries to fetch data using a list of tickers until a non-empty result is found.
    """
    for ticker in FULL_UNIVERSE:
        try:
            df = func_factory(ticker)()
            if df is not None and (isinstance(df, dict) or not df.empty):
                return df, ticker
        except:
            continue
    return None, None

def generate_markdown(all_data, version, timestamp, industry_groups):
    md = "# Vnstock Data Schema Snapshot\n\n"
    md += f"**Version**: `{version}`  \n"
    md += f"**Generated At**: `{timestamp}`  \n\n"
    md += "This document provides a comprehensive reference for the data structures and sample data returned by the Unified UI functions.\n\n"

    md += "# 1. Core UI Functions\n\n"
    sorted_notations = sorted([k for k in all_data.keys() if "Fundamental" not in k])
    for notation in sorted_notations:
        data = all_data[notation]
        md += f"## `{data['notation']}`\n"
        md += f"- **Module Context**: `{data['module']}`\n"
        if data.get('ticker_used'):
            md += f"- **Sample Ticker Used**: `{data['ticker_used']}`\n"
        md += "\n### Schema\n"
        md += "| Column | Type |\n|--------|------|\n"
        for col, dtype in data['dtypes'].items():
            md += f"| {col} | {dtype} |\n"
        md += "\n### Sample Data\n```json\n" + json.dumps(data['sample'], indent=2, ensure_ascii=False) + "\n```\n\n---\n\n"

    md += "# 2. Financial Statements by Industry\n\n"
    for group_name, tickers in industry_groups.items():
        md += f"## Industry: {group_name}\n"
        md += f"Representative Tickers: {', '.join(tickers)}\n\n"

        for statement in ["income_statement", "balance_sheet", "cash_flow", "ratio"]:
            found = False
            for ticker in tickers:
                key = f"Fundamental().equity('{ticker}').{statement}()"
                if key in all_data and all_data[key]['sample']:
                    data = all_data[key]
                    md += f"### {group_name} - {statement.replace('_', ' ').title()}\n"
                    md += f"- **Example Notation**: `{data['notation']}`\n"
                    md += f"- **Sample Ticker Used**: `{data['ticker_used']}`\n"
                    md += f"- **Module Context**: `{data['module']}`\n\n"
                    md += "#### Schema\n"
                    md += "| Column | Type |\n|--------|------|\n"
                    for col, dtype in data['dtypes'].items():
                        md += f"| {col} | {dtype} |\n"
                    md += "\n#### Sample Data\n```json\n" + json.dumps(data['sample'], indent=2, ensure_ascii=False) + "\n```\n\n"
                    found = True
                    break
        md += "---\n\n"

    return md

def main():
    os.makedirs('assets/data/schemas', exist_ok=True)
    all_snapshots = {}

    version = get_project_version()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    industry_groups = {
        "Banking": ["VCB", "ACB", "TCB", "CTG"],
        "Securities": ["SSI", "VCI", "HCM"],
        "Insurance": ["BVH", "PVI", "PTI"],
        "Regular": ["FPT", "VIC", "HPG", "NVL"]
    }

    # 1. Diversity-heavy tasks (try universe)
    diversity_tasks = [
        {"n": "Reference().company('{}').info()", "m": "Company Reference (KBS)", "f": lambda t: lambda: Reference().company(t).info()},
        {"n": "Reference().company('{}').shareholders()", "m": "Company Reference (KBS)", "f": lambda t: lambda: Reference().company(t).shareholders()},
        {"n": "Reference().company('{}').insider_trading()", "m": "Company Reference (KBS)", "f": lambda t: lambda: Reference().company(t).insider_trading()},
        {"n": "Reference().company('{}').news()", "m": "Company Reference (KBS)", "f": lambda t: lambda: Reference().company(t).news()},
        {"n": "Reference().company('{}').events()", "m": "Company Reference (KBS)", "f": lambda t: lambda: Reference().company(t).events()},
        {"n": "Reference().company('{}').officers()", "m": "Company Reference (KBS)", "f": lambda t: lambda: Reference().company(t).officers()},
        {"n": "Reference().company('{}').subsidiaries()", "m": "Company Reference (KBS)", "f": lambda t: lambda: Reference().company(t).subsidiaries()},
        {"n": "Reference().company('{}').ownership()", "m": "Company Reference (KBS)", "f": lambda t: lambda: Reference().company(t).ownership()},
        {"n": "Reference().company('{}').capital_history()", "m": "Company Reference (KBS)", "f": lambda t: lambda: Reference().company(t).capital_history()},
    ]

    for task in diversity_tasks:
        print(f"Generating snapshot for: {task['n'].format('UNIVERSE')}")
        df, ticker = try_fetch_with_universe(task['f'])
        if df is not None:
            notation = task['n'].format(ticker)
            meta = get_metadata(df, notation, task['m'], ticker_used=ticker)
            all_snapshots[notation] = meta
            filename = task['n'].format('DATA').replace('()', '').replace("'", "").replace('.', '_').replace('(', '_').replace(')', '').replace('{}', '')
            with open(f'assets/data/schemas/{filename}.json', 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
        else:
            print(f"WARNING: Could not find non-empty data for {task['n'].format('UNIVERSE')}")

    # 2. Static / One-off tasks
    static_tasks = [
        {"n": "Reference().equity.list()", "m": "Equity Reference (KBS)", "f": lambda: Reference().equity.list()},
        {"n": "Reference().industry.list()", "m": "Industry Reference (VCI)", "f": lambda: Reference().industry.list(source='vci')},
        {"n": "Market().quote('SSI')", "m": "Market Global Quote (KBS)", "f": lambda: Market().quote('SSI')},
        {"n": "Market().equity('SSI').ohlcv()", "m": "Equity Market (KBS)", "f": lambda: Market().equity('SSI').ohlcv()},
        {"n": "Market().index('VN30').ohlcv()", "m": "Index Market (KBS)", "f": lambda: Market().index('VN30').ohlcv()},
    ]

    for task in static_tasks:
        notation = task['n']
        print(f"Generating snapshot for: {notation}")
        try:
            df = task['f']()
            meta = get_metadata(df, notation, task['m'])
            if meta:
                all_snapshots[notation] = meta
                filename = notation.replace('()', '').replace("'", "").replace('.', '_').replace('(', '_').replace(')', '')
                with open(f'assets/data/schemas/{filename}.json', 'w', encoding='utf-8') as f:
                    json.dump(meta, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error snapshotting {notation}: {e}")

    # 3. Industry Fundamental Tasks
    for group_name, tickers in industry_groups.items():
        for ticker in tickers:
            for statement in ["income_statement", "balance_sheet", "cash_flow", "ratio"]:
                notation = f"Fundamental().equity('{ticker}').{statement}()"
                print(f"Generating snapshot for: {notation}")
                try:
                    df = getattr(Fundamental().equity(ticker), statement)()
                    meta = get_metadata(df, notation, f"Fundamental ({group_name})", ticker_used=ticker)
                    if meta:
                        all_snapshots[notation] = meta
                        filename = notation.replace('()', '').replace("'", "").replace('.', '_').replace('(', '_').replace(')', '')
                        with open(f'assets/data/schemas/{filename}.json', 'w', encoding='utf-8') as f:
                            json.dump(meta, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    print(f"Error snapshotting {notation}: {e}")

    md_content = generate_markdown(all_snapshots, version, timestamp, industry_groups)
    os.makedirs('docs', exist_ok=True)
    with open('docs/SNAPSHOT.md', 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"Success! Snapshot generated in docs/SNAPSHOT.md for version {version} at {timestamp}.")

if __name__ == "__main__":
    main()
