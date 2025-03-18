import requests
import json
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from vnstock.core.utils.user_agent import get_headers
from vnai import optimize_execution

@optimize_execution('MISC')
def sjc_gold_price(date=None):
    """
    Truy xuất giá vàng từ trang chủ SJC.

    Args:
        - date: Ngày tra cứu, mặc định là None để lấy ngày hiện tại. 
                Nhập giá trị tùy chọn, định dạng YYYY-mm-dd, ví dụ 2025-01-15.
                Dữ liệu có sẵn từ ngày 2/1/2016.

    Returns:
        - Pandas DataFrame chứa thông tin giá vàng nếu thành công, ngược lại trả về None.
    """
    # Set URL
    url = "https://sjc.com.vn/GoldPrice/Services/PriceService.ashx"

    # Define the minimum allowed date
    min_date = datetime(2016, 1, 2)

    # Convert date to required format DD/MM/YYYY
    if date is None:
        input_date = datetime.now().date()
    else:
        try:
            input_date = datetime.strptime(date, "%Y-%m-%d")
            if input_date < min_date:
                raise ValueError("Ngày tra cứu phải từ 2/1/2016 trở đi.")
        except ValueError:
            raise ValueError("Định dạng ngày không hợp lệ. Vui lòng nhập theo định dạng YYYY-mm-dd.")

    # Format date for the API request
    formatted_date = input_date.strftime("%d/%m/%Y")

    # Prepare request payload and headers
    payload = f"method=GetSJCGoldPriceByDate&toDate={formatted_date}"
    headers = get_headers(data_source='SJC', random_agent=False)

    # Send request
    response = requests.post(url, headers=headers, data=payload)

    # Handle response
    if response.status_code == 200:
        data = response.json()
        if not data.get("success"):
            print("Lỗi: Không thể truy xuất dữ liệu từ API.")
            return None

        gold_data = data.get("data", [])
        if not gold_data:
            print("Lỗi: Không có dữ liệu trả về từ API.")
            return None

        # Convert to DataFrame
        df = pd.DataFrame(gold_data)
        df = df[["TypeName", "BranchName", "BuyValue", "SellValue"]]
        df.columns = ["name", "branch", "buy_price", "sell_price"]

        # Add date column as datetime type
        df["date"] = input_date

        # Ensure numerical columns are correctly formatted
        df["buy_price"] = df["buy_price"].astype(float)
        df["sell_price"] = df["sell_price"].astype(float)

        return df
    else:
        print(f"Lỗi: Không thể kết nối đến API. Mã trạng thái: {response.status_code}")
        return None
    

@optimize_execution('MISC')
def btmc_goldprice(url='http://api.btmc.vn/api/BTMCAPI/getpricebtmc?key=3kd8ub1llcg9t45hnoh8hmn7t5kc2v'):
    """Parse dữ liệu giá vàng từ API JSON Bảo Tín Minh Châu.

    Args:
        url: Đường dẫn đến API JSON.

    Returns:
        DataFrame chứa dữ liệu giá vàng.
    """
    response = requests.get(url)
    json_data = response.json()
    data_list = json_data['DataList']['Data']

    data = []
    for item in data_list:
        row_number = item["@row"]
        n_key = f'@n_{row_number}'
        k_key = f'@k_{row_number}'
        h_key = f'@h_{row_number}'
        pb_key = f'@pb_{row_number}'
        ps_key = f'@ps_{row_number}'
        pt_key = f'@pt_{row_number}'
        d_key = f'@d_{row_number}'
        data.append({
            "name": item.get(n_key, ''),
            "karat": item.get(k_key, ''),
            "gold_content": item.get(h_key, ''),
            "buy_price": item.get(pb_key, ''),
            "sell_price": item.get(ps_key, ''),
            "world_price": item.get(pt_key, ''),
            "time": item.get(d_key, '')
        })
    df = pd.DataFrame(data)
    df = df.sort_values(by=['sell_price'], ascending=False)
    return df