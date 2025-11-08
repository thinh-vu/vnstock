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
    Checks for newer versions of vnstock and vnai packages and displays update notices.
    """
    packages = ["vnstock", "vnai"]
    
    try:
        environment = detect_environment()
        
        for package in packages:
            try:
                installed_version = get_version(package)
                response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=5)
                response.raise_for_status()
                latest_version = response.json().get("info", {}).get("version")

                if latest_version and version.parse(installed_version) < version.parse(latest_version):
                    package_name = package.capitalize()
                    # Customize URL based on package
                    if package == "vnstock":
                        history_url = (
                            "https://vnstocks.com/docs/"
                            "release-history"
                        )
                    else:
                        history_url = (
                            "https://pypi.org/project/vnai/"
                            "#history"
                        )
                    
                    msg = (
                        f"Version {package_name} {latest_version} "
                        f"is available. Please update using: "
                        f"`pip install {package} --upgrade`.\n"
                        f"Release history: {history_url}\n"
                        f"Current version: {installed_version}"
                    )

                    if (environment in ["Jupyter", "Google Colab"]
                            and ipython_available):
                        # Display as markdown in Jupyter
                        display(Markdown(msg))
                    else:
                        warnings.simplefilter(
                            "always", UserWarning
                        )
                        # Remove markdown styling for
                        # non-notebook environments
                        warnings.warn(
                            msg.replace("**", ""),
                            UserWarning,
                            stacklevel=2
                        )
            except (
                requests.exceptions.RequestException,
                ImportError,
                Exception  # Catch any other import-related errors
            ):
                # Skip this package if it's not installed or can't be checked
                pass
    except Exception:
        # Ensure the entire update check doesn't break the user's code
        pass

# Customizing the warnings output format for non-notebook environments


def custom_formatwarning(message, category, filename, lineno, line=None):
    return f"{message}\n"


warnings.formatwarning = custom_formatwarning
