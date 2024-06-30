from vnstock3.core.config.const import ID_DIR
import json
import sys

def get_platform():
    """
    Truy xuất tên hệ điều hành đang chạy
    """
    import platform
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

    

