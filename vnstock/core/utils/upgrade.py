import warnings
import requests
from packaging import version
from importlib.metadata import version as get_version
import sys
import os
import uuid
import re
import time

# Try to import IPython for Jupyter notebook/Google Colab support
try:
    from IPython.display import display, Markdown, HTML
    ipython_available = True
except ImportError:
    ipython_available = False

# Import version requirements and notices from config
try:
    from vnstock.config import (
        VERSION_REQUIREMENTS,
        VERSION_NOTICES,
        PYTHON_VERSION_SUPPORT,
    )
except ImportError:
    # Fallback if constants not available
    VERSION_REQUIREMENTS = {}
    VERSION_NOTICES = {}
    PYTHON_VERSION_SUPPORT = {}

# Global state for lazy checking
_notice_check_done = False
_last_check_time = 0
_check_interval = 3600  # Check once per hour

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

def _check_dependency_compatibility():
    """
    Check if installed dependencies meet the requirements for current vnstock version.
    Returns a tuple: (has_issues, critical_issues, warnings)
    Priority packages (vnai, vnii) are checked and displayed first.
    """
    from packaging.specifiers import SpecifierSet
    
    critical_issues = []
    warnings_list = []
    priority_packages = ["vnai", "vnii"]  # Always check and display first
    
    try:
        vnstock_version = get_version("vnstock").strip()
        
        # Get requirements for this version
        requirements = VERSION_REQUIREMENTS.get(vnstock_version, {})
        if not requirements:
            return False, [], []
        
        # Check priority packages first
        for package in priority_packages:
            if package not in requirements:
                continue
                
            version_spec = requirements[package]
            try:
                installed_version = get_version(package).strip()
                parsed_installed = version.parse(installed_version)
                
                # Parse version specifier (e.g., ">=2.2.3,<3.0.0")
                try:
                    spec_set = SpecifierSet(version_spec)
                    if parsed_installed not in spec_set:
                        critical_issues.append(
                            f"{package}: {installed_version} (requires {version_spec})"
                        )
                except Exception:
                    # Fallback to simple version comparison
                    parsed_required = version.parse(version_spec.lstrip(">=<!=~"))
                    if parsed_installed < parsed_required:
                        critical_issues.append(
                            f"{package}: {installed_version} (requires {version_spec})"
                        )
            except Exception:
                # Package not installed
                # vnai: always show (critical)
                # vnii: don't show if not installed (optional)
                if package == "vnai":
                    critical_issues.append(
                        f"{package}: not installed (requires {version_spec})"
                    )
        
        # Check other dependencies
        for package, version_spec in requirements.items():
            if package in priority_packages:
                continue  # Already checked above
                
            try:
                installed_version = get_version(package).strip()
                parsed_installed = version.parse(installed_version)
                
                # Parse version specifier
                try:
                    spec_set = SpecifierSet(version_spec)
                    if parsed_installed not in spec_set:
                        critical_issues.append(
                            f"{package}: {installed_version} (requires {version_spec})"
                        )
                except Exception:
                    # Fallback to simple version comparison
                    parsed_required = version.parse(version_spec.lstrip(">=<!=~"))
                    if parsed_installed < parsed_required:
                        critical_issues.append(
                            f"{package}: {installed_version} (requires {version_spec})"
                        )
            except Exception:
                # Package not installed
                critical_issues.append(
                    f"{package}: not installed (requires {version_spec})"
                )
        
        # Check version-specific notices - but merge with priority package issues
        notices = VERSION_NOTICES.get(vnstock_version, {})
        if notices:
            if notices.get("critical_notices"):
                # Filter out duplicate vnai notices
                for notice in notices["critical_notices"]:
                    if "vnai" not in notice.lower() or not any("vnai" in issue for issue in critical_issues):
                        critical_issues.append(notice)
            if notices.get("warnings"):
                warnings_list.extend(notices["warnings"])
        
        # Check Python version compatibility
        supported_py_versions = PYTHON_VERSION_SUPPORT.get(vnstock_version, [])
        if supported_py_versions:
            current_py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            if current_py_version not in supported_py_versions:
                warnings_list.append(
                    f"Python {current_py_version} not officially supported (requires {', '.join(supported_py_versions)})"
                )
        
        has_issues = bool(critical_issues or warnings_list)
        return has_issues, critical_issues, warnings_list
        
    except Exception:
        return False, [], []


def _display_message(msg, environment, is_warning=False):
    """
    Display message in appropriate format based on environment.
    """
    if environment in ["Jupyter", "Google Colab"] and ipython_available:
        display(Markdown(msg))
    else:
        warnings.simplefilter("always", UserWarning)
        warnings.warn(
            msg.replace("**", "").replace("`", ""),
            UserWarning,
            stacklevel=3
        )


def _check_version_updates():
    """
    Check for newer versions of packages and display update notices.
    """
    core_packages = ["vnstock", "vnai"]
    license_packages = ["vnii", "vnstock_installer"]
    environment = detect_environment()
    
    # Check core packages
    for package in core_packages:
        try:
            installed_version = get_version(package).strip()
            
            response = requests.get(
                f"https://pypi.org/pypi/{package}/json",
                timeout=5
            )
            response.raise_for_status()
            latest_version = response.json().get("info", {}).get("version", "").strip()
            
            if latest_version:
                parsed_installed = version.parse(installed_version)
                parsed_latest = version.parse(latest_version)
                
                if parsed_installed < parsed_latest:
                    package_name = package.capitalize()
                    history_url = (
                        "https://vnstocks.com/docs/tai-lieu/lich-su-phien-ban"
                        if package == "vnstock"
                        else "https://pypi.org/project/vnai/#history"
                    )
                    
                    msg = (
                        f"📦 **{package_name} {latest_version} is available**\n"
                        f"Current version: {installed_version}\n"
                        f"Update: `pip install {package} --upgrade`\n"
                        f"Release history: {history_url}"
                    )
                    _display_message(msg, environment)
        except (
            requests.exceptions.RequestException,
            ImportError,
            Exception
        ):
            pass
    
    # Check subscription packages
    for package in license_packages:
        try:
            installed_version = get_version(package).strip()
            latest_version = None
            
            if package == "vnii":
                try:
                    response = requests.get(
                        "https://vnstocks.com/api/simple/vnii",
                        timeout=5
                    )
                    if response.status_code == 200:
                        html = response.text
                        version_pattern = r'vnii-(\d+\.\d+\.\d+)\.tar\.gz'
                        versions = re.findall(version_pattern, html)
                        if versions:
                            latest_version = max(versions, key=version.parse)
                except:
                    pass
                
                update_cmd = (
                    "pip install --upgrade --extra-index-url "
                    "https://vnstocks.com/api/simple vnii"
                )
            
            elif package == "vnstock_installer":
                try:
                    response = requests.get(
                        "https://vnstocks.com/api/simple/vnstock-installer",
                        timeout=5
                    )
                    if response.status_code == 200:
                        html = response.text
                        version_pattern = r'vnstock[_-]installer-(\d+\.\d+\.\d+)\.tar\.gz'
                        versions = re.findall(version_pattern, html)
                        if versions:
                            latest_version = max(versions, key=version.parse)
                except:
                    pass
                
                update_cmd = (
                    "pip install --upgrade --extra-index-url "
                    "https://vnstocks.com/api/simple vnstock-installer"
                )
            
            if latest_version:
                latest_version = latest_version.strip()
                parsed_installed = version.parse(installed_version)
                parsed_latest = version.parse(latest_version)
                
                if parsed_installed < parsed_latest:
                    package_display = package.replace("_", " ").title()
                    msg = (
                        f"📦 **{package_display} {latest_version} is available** "
                        f"(subscription)\n"
                        f"Current version: {installed_version}\n"
                        f"Update: `{update_cmd}`"
                    )
                    _display_message(msg, environment)
        except ImportError:
            pass
        except (requests.exceptions.RequestException, Exception):
            pass


def update_notice(verbose=False):
    """
    Lazy-loaded notice system with smart caching.
    
    Args:
        verbose: If True, show all notices. If False, show only critical issues.
    """
    global _notice_check_done, _last_check_time
    
    try:
        current_time = time.time()
        
        # Skip if already checked recently (unless verbose)
        if not verbose and _notice_check_done and (current_time - _last_check_time) < _check_interval:
            return
        
        _last_check_time = current_time
        environment = detect_environment()
        
        # Check dependency compatibility
        has_issues, critical_issues, warnings_list = _check_dependency_compatibility()
        
        if has_issues and critical_issues:
            # Show compact critical issues only
            msg_parts = []
            msg_parts.append("⚠️  Dependency issues detected:")
            for issue in critical_issues[:3]:  # Show max 3 issues
                msg_parts.append(f"  • {issue}")
            
            if len(critical_issues) > 3:
                msg_parts.append(f"  ... and {len(critical_issues) - 3} more")
            
            msg_parts.append("\nFor details:\nfrom vnstock.core.utils.upgrade import show_full_notice\nshow_full_notice()")
            msg = "\n".join(msg_parts)
            _display_message(msg, environment, is_warning=True)
        
        # Only check updates if verbose or no critical issues
        if verbose or not critical_issues:
            _check_version_updates()
        
        _notice_check_done = True
        
    except Exception:
        # Silently fail - never break user code
        pass


def show_full_notice():
    """
    Show detailed dependency and update information.
    Call this manually when you want full diagnostics.
    """
    try:
        environment = detect_environment()
        
        # Check dependency compatibility
        has_issues, critical_issues, warnings_list = _check_dependency_compatibility()
        
        if has_issues:
            msg_parts = ["📋 **Full Dependency Report**\n"]
            
            if critical_issues:
                msg_parts.append("**❌ Critical Issues:**")
                for issue in critical_issues:
                    msg_parts.append(f"  • {issue}")
                msg_parts.append("")
            
            if warnings_list:
                msg_parts.append("**⚠️  Warnings:**")
                for warning in warnings_list:
                    msg_parts.append(f"  • {warning}")
                msg_parts.append("")
            
            msg_parts.append("**Resolution:**")
            msg_parts.append("  pip install -r requirements.txt --upgrade")
            
            msg = "\n".join(msg_parts)
            _display_message(msg, environment, is_warning=True)
        else:
            print("✅ All dependencies are compatible!")
        
        # Show available updates
        print("\n📦 Checking for available updates...")
        _check_version_updates()
        
    except Exception as e:
        print(f"Error showing full notice: {e}")

# Customizing the warnings output format for non-notebook environments


def custom_formatwarning(message, category, filename, lineno, line=None):
    return f"{message}\n"


warnings.formatwarning = custom_formatwarning
