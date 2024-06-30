from vnstock3.core.config.const import ID_DIR
import json
import sys

def get_platform():
    """
    Get the platform of the current system
    """
    import platform
    PLATFORM = platform.system()
    return PLATFORM

def get_package_path(package='vnstock'):
    """
    Get the path to the package directory
    """
    from importlib.util import find_spec
    spec = find_spec(package)
    if spec and spec.origin:
        package_path = spec.origin 
    elif spec and spec.submodule_search_locations:
        package_path = spec.submodule_search_locations[0]
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

    

