import json
from typing import Dict

def save_json(data: Dict, path: str = 'data.json'):
    """
    Lưu dữ liệu dưới dạng JSON.
    """
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)  # Indent for readability
        print(f"Information saved to JSON file: {path}")
    except Exception as e:
        print(f"Error saving data to JSON: {e}")


# Bổ sung hàm cho Sheets, AmiBroker, Numpy, JSON, Polars 