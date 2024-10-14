from datetime import datetime, timedelta
import os
import platform

def get_date(n, unit):
    """
    Return YYYY-mm-dd value from today to n days, months or years in the past
    Parameters:
        n: number of days, months or years
        unit: 'day', 'month' or 'year'
    """
    if unit == 'day':
        return (datetime.now() - timedelta(days=n)).strftime('%Y-%m-%d')
    elif unit == 'month':
        return (datetime.now() - relativedelta(months=n)).strftime('%Y-%m-%d')
    elif unit == 'year':
        return (datetime.now() - relativedelta(years=n)).strftime('%Y-%m-%d')

def get_username():
    try:
        username = os.getlogin()
        return username
    except OSError as e:
        print(f"Error: {e}")
        return None
    
def get_os():
    try:
        os = platform.system()
        return os
    except OSError as e:
        print(f"Error: {e}")
        return None

def get_cwd():
    """Return current working directory"""
    try:
        cwd = os.getcwd()
        return cwd
    except OSError as e:
        print(f"Error: {e}")
        return None

def get_path_delimiter():
    """
    Detect the running OS and return the appropriate file path delimiter.
    """
    return '\\' if os.name == 'nt' else '/'

# UPDATE NOTICE

import warnings
import requests
from packaging import version
from importlib.metadata import version as get_version
from IPython.display import display, Markdown, HTML
import sys
import os
import uuid

def detect_environment():
    """
    Detects the running environment (Jupyter, Google Colab, etc.) and returns a string identifier.
    """
    try:
        from IPython import get_ipython
        if 'IPKernelApp' not in get_ipython().config:
            if sys.stdout.isatty():
                return "Terminal"
            else:
                return "Other"  # Non-interactive environment (e.g., script executed from an IDE)
        else:
            if 'google.colab' in sys.modules:
                return "Google Colab"
            return "Jupyter"
    except (ImportError, AttributeError):
        if sys.stdout.isatty():
            return "Terminal"
        else:
            return "Other"

def detect_hosting_service():
    """
    Detects if the code is running in a cloud environment (Google Colab, Kaggle, etc.)
    """
    try:
        if 'google.colab' in sys.modules:
            return "Google Colab"
        elif 'CODESPACE_NAME' in os.environ:
            return "Github Codespace"
        elif 'GITPOD_WORKSPACE_CLUSTER_HOST' in os.environ:
            return "Gitpod"
        elif 'REPLIT_USER' in os.environ:
            return "Replit"
        elif 'KAGGLE_CONTAINER_NAME' in os.environ:
            return "Kaggle"
        elif 'SPACE_HOST' in os.environ and '.hf.space' in os.environ['SPACE_HOST']:
            return "Hugging Face Spaces"
        else:
            return "Local or Unknown"
    except:
        return "Local or Unknown"

def update_notice():
    """
    Checks for a newer version of the package and displays an update notice.
    """
    try:
        installed_version = get_version("vnstock")
        response = requests.get("https://pypi.org/pypi/vnstock3/json", timeout=5)
        response.raise_for_status()
        latest_version = response.json().get("info", {}).get("version")

        if latest_version and version.parse(installed_version) < version.parse(latest_version):
            message = (
                f"**Vui lòng chuyển đổi sang Vnstock3** thế hệ mới ({latest_version}) với câu lệnh: `pip install vnstock3 --upgrade`.\n"
                "**Từ 1/1/2025, vnstock3 sẽ được cài đặt khi sử dụng cú pháp** `pip install vnstock` **thay cho Vnstock Legacy** hiện tại.\n"
                "Xem chi tiết [chuyển đổi sang vnstock3](https://vnstocks.com/docs/tai-lieu/migration-chuyen-doi-sang-vnstock3).\n"
                f"Phiên bản **Vnstock Legacy ({installed_version})** bạn đang sử dụng **sẽ không được nâng cấp thêm.**\n"
                "Từ 7/10/2024 Vnstock giới thiệu nhóm Facebook Cộng đồng Vnstock, tham gia thảo luận tại đây: https://www.facebook.com/groups/vnstock.official"
            )

            environment = detect_environment()

            if environment in ["Jupyter", "Google Colab"]:
                display(Markdown(message))  # Display as markdown in Jupyter or Google Colab
            else:
                warnings.simplefilter("always", UserWarning)
                warnings.warn(
                    message.replace("**", ""),  # Remove markdown styling for non-notebook environments
                    UserWarning,
                    stacklevel=2
                )
    except requests.exceptions.RequestException:
        pass

# Customizing the warnings output format for non-notebook environments
def custom_formatwarning(message, category, filename, lineno, line=None):
    return f"{message}\n"

warnings.formatwarning = custom_formatwarning