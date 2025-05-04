from vnstock.core.config.const import ID_DIR
import sys
import json
import os
import platform
import vnai

def get_platform():
    """
    Truy xuất tên hệ điều hành đang chạy
    """
    PLATFORM = platform.system()
    return PLATFORM

def get_hosting_service():
    """
    Xác định dịch vụ đám mây đang chạy hoặc môi trường phát triển
    """
    try:
        if 'google.colab' in sys.modules:
            hosting_service = "Google Colab"
        elif 'CODESPACE_NAME' in os.environ:
            hosting_service = "Github Codespace"
        elif 'GITPOD_WORKSPACE_CLUSTER_HOST' in os.environ:
            hosting_service = "Gitpod"
        elif 'REPLIT_USER' in os.environ:
            hosting_service = "Replit"
        elif 'KAGGLE_CONTAINER_NAME' in os.environ:
            hosting_service = "Kaggle"
        elif '.hf.space' in os.environ['SPACE_HOST']:
            hosting_service = "Hugging Face Spaces"
    except:
        hosting_service = "Local or Unknown"
    return hosting_service

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
    """
    Check if license terms have been accepted.
    """
    from vnai.scope.profile import inspector
    machine_id = inspector.fingerprint()
    
    pkg_init = ID_DIR / "environment.json"
    try:
        with open(pkg_init, 'r') as f:
            env = json.load(f)
        if not env['accepted_agreement']:
            # Use vnai to accept terms
            vnai.accept_license_terms()
    except:
        # Use vnai to accept terms
        vnai.accept_license_terms()
    
    return True
   
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
