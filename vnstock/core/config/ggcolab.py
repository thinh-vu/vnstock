"""
Google Colab Integration Module

Centralized management of all Google Colab-related logic:
- Google Drive mounting
- Persistent storage configuration
- Environment detection
- Data migration between local and Drive
"""

import os
import sys
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTS
# ============================================================================

COLAB_DRIVE_MOUNT_PATH = "/content/drive"
# Config, license, user data
COLAB_VNSTOCK_DIR = "/content/drive/MyDrive/.vnstock"
# Isolated package directory (not a true venv, but acts as target for pip
# install via --target flag. Packages are added to sys.path)
COLAB_VENV_DIR = "/content/drive/MyDrive/.venv"


# ============================================================================
# ENVIRONMENT DETECTION
# ============================================================================

def is_google_colab() -> bool:
    """
    Check if running on Google Colab.
    Reuses logic from get_hosting_service()
    
    Returns:
        bool: True if on Google Colab
    """
    try:
        from vnstock.core.utils.env import get_hosting_service
        return get_hosting_service() == "Google Colab"
    except Exception:
        # Fallback: check directly
        return 'google.colab' in sys.modules


def is_drive_mounted() -> bool:
    """
    Check if Google Drive is already mounted.

    Returns:
        bool: True if Drive is mounted
    """
    return os.path.exists(COLAB_DRIVE_MOUNT_PATH) and \
        os.path.ismount(COLAB_DRIVE_MOUNT_PATH)


# ============================================================================
# DRIVE MANAGEMENT
# ============================================================================

def mount_drive(force_remount: bool = False) -> bool:
    """
    Mount Google Drive.
    
    Handles case where mountpoint already contains files from previous
    sessions (cleanup/unmount as needed).
    
    Args:
        force_remount: Force remount even if already mounted
        
    Returns:
        bool: True if mount succeeded
    """
    if not is_google_colab():
        logger.debug("Not on Google Colab")
        return False
    
    if is_drive_mounted() and not force_remount:
        logger.debug("Google Drive already mounted")
        return True
    
    try:
        from google.colab import drive
        
        # If force_remount and already mounted, try to unmount first
        if is_drive_mounted() and force_remount:
            try:
                subprocess.run(
                    ["sudo", "umount", COLAB_DRIVE_MOUNT_PATH],
                    check=False
                )
                logger.debug("Unmounted Drive for remount")
            except Exception as e:
                logger.debug(f"Unmount attempt: {e}")

        # If mountpoint has files, try to clean up
        mount_path = Path(COLAB_DRIVE_MOUNT_PATH)
        if mount_path.exists() and any(mount_path.iterdir()):
            logger.debug(
                f"Mountpoint {COLAB_DRIVE_MOUNT_PATH} has files, "
                "attempting cleanup"
            )
            try:
                subprocess.run(
                    ["sudo", "rm", "-rf", COLAB_DRIVE_MOUNT_PATH],
                    check=False
                )
                logger.debug("Cleaned up mountpoint")
            except Exception as e:
                logger.debug(f"Cleanup attempt: {e}")
        
        print("\n📋 Connecting Google Drive account")
        print("to save project settings.\n")
        
        drive.mount(
            COLAB_DRIVE_MOUNT_PATH,
            force_remount=force_remount
        )
        logger.info(
            f"Drive mounted successfully: {COLAB_DRIVE_MOUNT_PATH}"
        )
        return True
        
    except Exception as e:
        logger.error(f"Error mounting Drive: {e}")
        return False


def initialize_colab_environment() -> bool:
    """
    Initialize Colab environment:
    - Mount Drive if not already mounted (with cleanup if needed)
    - Create .vnstock directory (config, license, user data)
    - Create .venv directory (pip install --target packages, added to
      sys.path)
    - Add both directories to sys.path for imports

    Note: .venv is NOT a true virtual environment on Colab. It's an
    isolated directory where packages are installed via pip --target
    flag. Packages are loaded by adding the directory to sys.path,
    NOT by activating an env.

    Returns:
        bool: True if successful
    """
    if not is_google_colab():
        return False

    # Mount Drive - try with cleanup if needed
    if not is_drive_mounted():
        if not mount_drive(force_remount=True):
            logger.warning("Cannot mount Drive, fallback to local")
            return False
    
    try:
        # Create .vnstock directory for config/license/user data
        os.makedirs(COLAB_VNSTOCK_DIR, exist_ok=True)
        logger.info(f"Vnstock data directory: {COLAB_VNSTOCK_DIR}")

        # Create .venv directory for isolated pip packages
        os.makedirs(COLAB_VENV_DIR, exist_ok=True)
        logger.info(f"Isolated packages directory: {COLAB_VENV_DIR}")

        # Add both to sys.path (packages loaded via path, not env
        # activation)
        if COLAB_VNSTOCK_DIR not in sys.path:
            sys.path.insert(0, COLAB_VNSTOCK_DIR)
            logger.info(f"Added to sys.path: {COLAB_VNSTOCK_DIR}")

        if COLAB_VENV_DIR not in sys.path:
            sys.path.insert(0, COLAB_VENV_DIR)
            logger.info(f"Added to sys.path: {COLAB_VENV_DIR}")

        return True

    except Exception as e:
        logger.error(f"Error initializing Colab environment: {e}")
        return False


# ============================================================================
# DIRECTORY RESOLUTION
# ============================================================================

def get_vnstock_directory() -> Path:
    """
    Determine .vnstock directory based on environment.
    Prioritizes Google Drive when on Colab.
    
    Returns:
        Path: Path to .vnstock directory
    """
    if is_google_colab():
        drive_path = Path(COLAB_VNSTOCK_DIR)
        
        # Check if Drive is mounted
        if drive_path.exists():
            # Add to sys.path if not already present
            if str(drive_path) not in sys.path:
                sys.path.insert(0, str(drive_path))
            logger.debug(f"Using Colab Drive path: {drive_path}")
            return drive_path
        
        # Try auto-mount
        if initialize_colab_environment():
            return drive_path
        
        logger.debug("Drive not available, fallback to local")
    
    # Default: home directory
    local_path = Path.home() / ".vnstock"
    logger.debug(f"Using local path: {local_path}")
    return local_path


def get_vnstock_data_dir() -> Path:
    """
    Return vnstock data storage directory.
    Prioritizes VNSTOCK_DATA_DIR environment variable.
    
    Returns:
        Path: Path to data directory
    """
    # Check environment variable first
    data_dir = os.environ.get("VNSTOCK_DATA_DIR")
    if data_dir:
        return Path(data_dir).expanduser().resolve()
    
    # Fallback to get_vnstock_directory()
    return get_vnstock_directory()


# ============================================================================
# INSTALLATION & SETUP
# ============================================================================

def get_install_target() -> Optional[str]:
    """
    Get target path for pip install (isolated packages directory).
    
    On Colab, packages are installed to .venv using:
        pip install --target=/content/drive/MyDrive/.venv vnstock
    
    This directory is added to sys.path for imports, NOT activated
    as a virtual environment.
    
    Returns:
        Optional[str]: Path to .venv if on Colab, None if local
    """
    if is_google_colab() and is_drive_mounted():
        return COLAB_VENV_DIR
    return None


def show_setup_guide() -> None:
    """Display setup guide for user"""
    if not is_google_colab():
        return
    
    print("\n" + "="*70)
    print("🚀 VNSTOCK ON GOOGLE COLAB")
    print("="*70)
    print("\n📦 To install vnstock to isolated packages dir (one-time only):")
    print(f"\n  !pip install --target={COLAB_VENV_DIR} vnstock\n")
    print("🔄 In subsequent sessions (packages auto-loaded from sys.path):")
    print("\n  from vnstock.core.config.ggcolab import")
    print("  initialize_colab_environment")
    print("  initialize_colab_environment()")
    print("  import vnstock")
    print("\n" + "="*70 + "\n")


def get_install_command() -> str:
    """
    Get pip install command for Colab.
    Packages are installed to .venv and loaded via sys.path.
    """
    if not is_google_colab():
        return ""
    return f"!pip install --target={COLAB_VENV_DIR} vnstock"


# ============================================================================
# DATA MIGRATION
# ============================================================================

def migrate_vnstock_data_colab(new_dir: Optional[str] = None) -> bool:
    """
    Migrate ~/.vnstock data to Google Drive (Colab only).
    Only copies config, license, and user data to .vnstock directory.
    
    Args:
        new_dir: Path to new directory (default: COLAB_VNSTOCK_DIR)
        
    Returns:
        bool: True if migration succeeded
        
    Raises:
        RuntimeError: If not on Google Colab
    """
    if not is_google_colab():
        raise RuntimeError("This function is for Google Colab only")
    
    # Mount Drive
    if not mount_drive():
        raise RuntimeError("Cannot mount Google Drive")
    
    # Use default directory if not specified
    if new_dir is None:
        new_dir = COLAB_VNSTOCK_DIR
    
    if not isinstance(new_dir, (str, Path)):
        raise TypeError("new_dir must be string or Path")
    
    old_dir = Path.home() / ".vnstock"
    new_dir = Path(new_dir).expanduser().resolve()
    
    # Check if old directory exists
    if not old_dir.exists():
        logger.warning(f"Old directory does not exist: {old_dir}")
        return False
    
    # Check if parent directory exists
    if not new_dir.parent.exists():
        msg = f"Parent directory of {new_dir} does not exist"
        raise FileNotFoundError(msg)
    
    # Create new directory
    os.makedirs(new_dir, exist_ok=True)
    
    # Copy data (config, license, user data only)
    try:
        for item in old_dir.iterdir():
            dest = new_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
        
        logger.info(f"Data migration successful: {new_dir}")
        
        # Set environment variable
        os.environ['VNSTOCK_DATA_DIR'] = str(new_dir)
        print(f"✅ Data migrated to: {new_dir}")
        print(f"✅ VNSTOCK_DATA_DIR={new_dir}")
        
        return True
        
    except (shutil.Error, OSError) as e:
        logger.error(f"Error copying data: {e}")
        raise RuntimeError(f"Error migrating data: {e}")


# ============================================================================
# HELPER FUNCTIONS (COMPATIBILITY)
# ============================================================================

def setup_colab_drive(auto_mount: bool = True) -> bool:
    """
    Setup Google Drive (Compatibility wrapper).
    
    Args:
        auto_mount: Auto-mount if not already mounted
        
    Returns:
        bool: True if setup succeeded
    """
    if not is_google_colab():
        return False
    
    if auto_mount:
        return initialize_colab_environment()
    
    return is_drive_mounted()


# ============================================================================
# MANAGER CLASS
# ============================================================================

class ColabManager:
    """Manager for Google Colab operations"""
    
    def __init__(self):
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize Colab environment"""
        if self._initialized:
            return True
        
        success = initialize_colab_environment()
        if success:
            self._initialized = True
        
        return success
    
    @property
    def vnstock_path(self) -> Path:
        """Get .vnstock directory path"""
        return get_vnstock_directory()
    
    @property
    def install_target(self) -> Optional[str]:
        """Get target for pip install"""
        return get_install_target()
    
    def show_guide(self) -> None:
        """Display setup guide"""
        show_setup_guide()
    
    def migrate_data(self, new_dir: Optional[str] = None) -> bool:
        """Migrate data"""
        try:
            return migrate_vnstock_data_colab(new_dir)
        except Exception as e:
            logger.error(f"Error during migration: {e}")
            return False


# Singleton instance
_manager: Optional[ColabManager] = None


def get_manager() -> ColabManager:
    """Get singleton instance of ColabManager"""
    global _manager
    if _manager is None:
        _manager = ColabManager()
    return _manager
