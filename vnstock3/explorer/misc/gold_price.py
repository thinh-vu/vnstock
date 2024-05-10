import requests
import json
from bs4 import BeautifulSoup
import pandas as pd


def sjc_gold_price(url='https://sjc.com.vn/giavang/textContent.php'):
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        update_time = soup.find('div', class_='w350').get_text(strip=True)
        currency_unit = soup.find('div', class_='float_left ylo_text', style='font-size:26px').get_text(strip=True)

        print("Cập nhật lúc:", update_time)
        print("Đơn vị tính:", currency_unit)

        table = soup.find('div', class_='bx1').find('table')

        data = []
        headers = []
        for row in table.find_all('tr'):
            row_data = []
            for cell in row.find_all(['td', 'th']):
                row_data.append(cell.get_text(strip=True))
            if not headers:
                headers = row_data
            else:
                data.append(row_data)

        df = pd.DataFrame(data, columns=headers)
        df = df.query("`Loại vàng` != ''")
        df = df.rename(columns={"Loại vàng": "name", "Mua": "buy_price", "Bán": "sell_price"})
        df['name'] = df['name'].str.replace('SJC 99,99', 'SJC 99,99 | ')
        return df

    else:
        print(f"Failed to retrieve content. Status code: {response.status_code}")
        return None
    

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