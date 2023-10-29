# DNSE API: https://www.dnse.vn
from .config import *

def dnse_login(user_name, password):
    """
    Get JWT token from DNSE to authenticate other API requests. Return a JWT token as a string.
    Parameters:
        user_name (str): DNSE username. Can be 064CXXXXX, your email or your phone number. Refer to the detailed API document here: https://s.dnse.vn/api_doc
        password (str): Your DNSE password.
    """
    url = "https://services.entrade.com.vn/dnse-user-service/api/auth"
    payload = json.dumps({'username': f'{user_name}','password': f'{password}'})
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    status = response.status_code
    if status == 200:
        print('Login successfully')
        return response.json()['token']
    else:
        print('Login failed')
        return None


def dnse_profile(token):
    """
    Get full user profile from DNSE. Return a Pandas DataFrame.
    Parameters:
        token (str): JWT token from DNSE. Use dnse_login() to get the token.
    """
    url = "https://services.entrade.com.vn/dnse-user-service/api/me"

    payload = "N/A"
    headers = {
    'Content-Type': 'text/plain',
    'Authorization': f'Bearer {token}'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    status = response.status_code
    if status == 200:
        print('Get profile successfully')
        df = pd.DataFrame(response.json(), index=[0])
        return df
    else:
        print('Get profile failed')
        return None