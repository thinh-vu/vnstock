from vnstock3.core.config.const import ID_DIR
import sys
import json
import os
import platform

def get_platform():
    """
    Truy xuất tên hệ điều hành đang chạy
    """
    PLATFORM = platform.system()
    return PLATFORM


def get_package_path(package='vnstock'):
    """
    Truy xuất đường dẫn của 1 gói Python bất kỳ
    """
    from importlib.util import find_spec
    spec = find_spec(package)
    if spec and spec.origin:
        package_path = spec.origin  # Path to the package's main file
    elif spec and spec.submodule_search_locations:
        package_path = spec.submodule_search_locations[0]  # Path to the package directory
    else:
        package_path = None
    return package_path


def id_valid():
    pkg_init = ID_DIR / "environment.json"
    try:
        with open(pkg_init, 'r') as f:
            env = json.load(f)
        if not env['accepted_agreement']:
            raise SystemExit('Bạn cần chấp thuận điều khoản, điều kiện để sử dụng Vnstock!')
    except:
        raise SystemExit('Bạn cần chấp thuận điều khoản, điều kiện để sử dụng Vnstock!')

    
def get_username():
    """
    Get the current username of the system.
    """
    try:
        username = os.getlogin()
        return username
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
