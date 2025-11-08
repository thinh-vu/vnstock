import sys
import json
import os
import platform
import vnai
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def get_vnstock_directory() -> Path:
    """
    Determine .vnstock directory based on environment.
    Reuses logic from core.config.ggcolab
    
    Returns:
        Path: Path to .vnstock directory
    """
    try:
        from vnstock.core.config.ggcolab import (
            get_vnstock_directory as ggcolab_get_vnstock_dir
        )
        return ggcolab_get_vnstock_dir()
    except ImportError:
        # Fallback if ggcolab not loaded yet
        return Path.home() / ".vnstock"


def is_colab() -> bool:
    """Check if running on Google Colab"""
    return get_hosting_service() == "Google Colab"


def setup_colab_drive(auto_mount: bool = True) -> bool:
    """
    Setup Google Drive for Colab environment.
    Reuses get_hosting_service() to detect Colab.
    
    Args:
        auto_mount: Auto-mount Drive if not already mounted
        
    Returns:
        bool: True if setup succeeded
    """
    if not is_colab():
        return False
    
    drive_path = Path("/content/drive/MyDrive/.vnstock")
    
    # Check if Drive already mounted
    if not drive_path.exists() and auto_mount:
        try:
            from google.colab import drive
            print("\n📋 Connecting Google Drive to save vnstock config.")
            print("You can reuse the project without reinstalling.\n")
            drive.mount('/content/drive')
        except Exception as e:
            print(f"Cannot mount Drive: {e}")
            return False
    
    # Create directory if not exists
    drive_path.mkdir(parents=True, exist_ok=True)
    
    # Add to sys.path
    if str(drive_path) not in sys.path:
        sys.path.insert(0, str(drive_path))
    
    return True


def get_colab_install_command() -> str:
    """Get install command for vnstock on Google Drive"""
    if not is_colab():
        return ""
    
    drive_path = "/content/drive/MyDrive/.vnstock"
    return f"!pip install --target={drive_path} vnstock"


def show_colab_instructions() -> None:
    """Display usage instructions for vnstock with Google Drive"""
    if not is_colab():
        return
    
    drive_path = "/content/drive/MyDrive/.vnstock"
    print("\n" + "="*70)
    print("🚀 VNSTOCK ON GOOGLE COLAB")
    print("="*70)
    print("\n📦 To install vnstock on Drive (one-time only):")
    print(f"\n  !pip install --target={drive_path} vnstock\n")
    print("🔄 In subsequent sessions, just run setup code:")
    print("\n  from vnstock.core.utils.env import setup_colab_drive")
    print("  setup_colab_drive()")
    print("  import vnstock")
    print("\n" + "="*70 + "\n")


def get_vnstock_path() -> Path:
    """
    Get .vnstock directory path.
    Auto-handles Colab Drive if available.
    """
    if is_colab():
        drive_path = Path("/content/drive/MyDrive/.vnstock")
        if drive_path.exists():
            return drive_path
    
    return Path.home() / ".vnstock"


def get_platform():
    """Get the name of the running operating system"""
    PLATFORM = platform.system()
    return PLATFORM

def get_hosting_service():
    """Identify cloud service or development environment currently running"""
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
    """Get the path of any Python package"""
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
    from vnstock.core.config.const import ID_DIR
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
