import pathlib


def _get_project_dir() -> pathlib.Path:
    """
    Get project directory from ggcolab module.
    Avoid circular import with lazy import.
    """
    try:
        # Lazy import from ggcolab
        from vnstock.core.config.ggcolab import get_vnstock_directory
        return get_vnstock_directory()
    except ImportError:
        # Fallback if ggcolab not loaded yet
        return pathlib.Path.home() / ".vnstock"


HOME_DIR = pathlib.Path.home()
PROJECT_DIR = _get_project_dir()
ID_DIR = PROJECT_DIR / 'id'

# Ensure directories exist
PROJECT_DIR.mkdir(parents=True, exist_ok=True)
ID_DIR.mkdir(parents=True, exist_ok=True)

TC_VAR = "ACCEPT_TC"
TC_VAL = "tôi đồng ý"

UA = {'Chrome' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
               'Opera' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0',
               'Edge' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
               'Firefox' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0'
               }