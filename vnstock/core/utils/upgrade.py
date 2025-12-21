import warnings
import requests
from packaging import version
from importlib.metadata import version as get_version
import sys
import os
import uuid
import re

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
    Checks for newer versions of vnstock, vnai, vnii (subscription), 
    and vnstock_installer (subscription) packages and displays update notices.
    """
    # Core packages (always check)
    core_packages = ["vnstock", "vnai"]
    
    # Subscription packages (only check if installed)
    license_packages = ["vnii", "vnstock_installer"]
    
    try:
        environment = detect_environment()
        
        # Check core packages
        for package in core_packages:
            try:
                installed_version = get_version(package)
                installed_version = installed_version.strip()
                
                response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=5)
                response.raise_for_status()
                latest_version = response.json().get("info", {}).get("version")
                
                if latest_version:
                    latest_version = latest_version.strip()
                    
                    try:
                        parsed_installed = version.parse(installed_version)
                        parsed_latest = version.parse(latest_version)
                        
                        # Only show update notice if there's a newer version
                        if parsed_installed < parsed_latest:
                            package_name = package.capitalize()
                            # Customize URL based on package
                            if package == "vnstock":
                                history_url = (
                                    "https://vnstocks.com/docs/tai-lieu/lich-su-phien-ban"
                                )
                            else:  # vnai
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
                    except Exception as parse_error:
                        # Log version parsing errors for debugging
                        pass
            except (
                requests.exceptions.RequestException,
                ImportError,
                Exception  # Catch any other import-related errors
            ):
                # Skip this package if it's not installed or can't be checked
                pass
        
        # Check subscription packages (only if installed)
        for package in license_packages:
            try:
                installed_version = get_version(package)
                installed_version = installed_version.strip()
                
                # For subscription packages, get version from vnstocks.com private index
                latest_version = None
                
                if package == "vnii":
                    # Check vnstocks.com private index for vnii
                    try:
                        response = requests.get(
                            "https://vnstocks.com/api/simple/vnii", 
                            timeout=5
                        )
                        if response.status_code == 200:
                            # Parse HTML to extract version from links like:
                            # <a href="...">vnii-X.Y.Z.tar.gz</a>
                            html = response.text
                            # Find all version patterns like vnii-0.1.2.tar.gz
                            version_pattern = r'vnii-(\d+\.\d+\.\d+)\.tar\.gz'
                            versions = re.findall(version_pattern, html)
                            if versions:
                                # Get the highest version
                                latest_version = max(versions, key=version.parse)
                    except:
                        pass
                    
                    history_url = "https://vnstocks.com/docs/tai-lieu/lich-su-phien-ban"
                    update_cmd = (
                        f"pip install --upgrade --extra-index-url "
                        f"https://vnstocks.com/api/simple {package}"
                    )
                
                elif package == "vnstock_installer":
                    # Check vnstocks.com private index for vnstock_installer
                    try:
                        response = requests.get(
                            "https://vnstocks.com/api/simple/vnstock-installer",
                            timeout=5
                        )
                        if response.status_code == 200:
                            # Parse HTML to extract version from links like:
                            # <a href="...">vnstock_installer-X.Y.Z.tar.gz</a>
                            # or <a href="...">vnstock-installer-X.Y.Z.tar.gz</a>
                            html = response.text
                            # Try both naming conventions
                            version_pattern = r'vnstock[_-]installer-(\d+\.\d+\.\d+)\.tar\.gz'
                            versions = re.findall(version_pattern, html)
                            if versions:
                                # Get the highest version
                                latest_version = max(versions, key=version.parse)
                    except:
                        pass
                    
                    history_url = "https://vnstocks.com/docs/tai-lieu/lich-su-phien-ban"
                    update_cmd = (
                        f"pip install --upgrade --extra-index-url "
                        f"https://vnstocks.com/api/simple vnstock-installer"
                    )
                
                if latest_version:
                    latest_version = latest_version.strip()
                    
                    try:
                        parsed_installed = version.parse(installed_version)
                        parsed_latest = version.parse(latest_version)
                        
                        # Only show update notice if there's a newer version
                        if parsed_installed < parsed_latest:
                            package_display = package.replace("_", " ").title()
                            
                            msg = (
                                f"Version {package_display} {latest_version} "
                                f"is available (subscription package). "
                                f"Please update using: `{update_cmd}`.\n"
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
                                warnings.warn(
                                    msg.replace("**", ""),
                                    UserWarning,
                                    stacklevel=2
                                )
                    except Exception as parse_error:
                        # Log version parsing errors for debugging
                        pass
            except ImportError:
                # Subscription package not installed - this is normal
                # Don't show any warning
                pass
            except (
                requests.exceptions.RequestException,
                Exception  # Catch any other errors
            ):
                # Skip this package if can't be checked
                pass
    except Exception:
        # Ensure the entire update check doesn't break the user's code
        pass

# Customizing the warnings output format for non-notebook environments


def custom_formatwarning(message, category, filename, lineno, line=None):
    return f"{message}\n"


warnings.formatwarning = custom_formatwarning
