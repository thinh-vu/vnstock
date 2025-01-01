import warnings
import requests
from packaging import version
from importlib.metadata import version as get_version
import sys
import os
import uuid

# Try to import IPython for Jupyter notebook/Google Colab support
try:
    from IPython.display import display, Markdown, HTML
    ipython_available = True
except ImportError:
    ipython_available = False

def detect_environment():
    """
    Detects the running environment (Jupyter, Google Colab, etc.) and returns a string identifier.
    """
    if ipython_available:
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
    else:
        if sys.stdout.isatty():
            return "Terminal"
        else:
            return "Other"

def update_notice():
    """
    Checks for a newer version of the package and displays an update notice.
    """
    try:
        installed_version = get_version("vnstock")
        response = requests.get("https://pypi.org/pypi/vnstock/json", timeout=5)
        response.raise_for_status()
        latest_version = response.json().get("info", {}).get("version")

        if latest_version and version.parse(installed_version) < version.parse(latest_version):
            message = (
                f"Phiên bản Vnstock {latest_version} đã có mặt, vui lòng cập nhật với câu lệnh : `pip install vnstock --upgrade`.\n"
                f"Lịch sử phiên bản: https://vnstocks.com/docs/tai-lieu/lich-su-phien-ban\n"
                f"Phiên bản hiện tại {installed_version}"
            )

            environment = detect_environment()

            if environment in ["Jupyter", "Google Colab"] and ipython_available:
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