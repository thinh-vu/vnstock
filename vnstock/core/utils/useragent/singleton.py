# singleton.py
# This file is used to create a singleton instance of the UserAgentManager class.

from user_agent_manager import UserAgentManager
from typing import Callable, List, Optional
import requests

_ua_manager_config = {
    "redownload": "lazy",
    "max_age_days": 7,
    "cache_path": None
}

_ua_manager_instance = None

# This is a helper function to fetch the user agent list from the microlink source.
def _microlink_source():
    try:
        url = "https://raw.githubusercontent.com/microlinkhq/top-user-agents/master/src/index.json"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[MicrolinkHQ] failed to fetch: {e}")
        return []

# This is a helper function to set the config for the UserAgentManager class.
def set_user_agent_manager_config(
    redownload: str = "lazy",
    max_age_days: int = 7,
    cache_path: Optional[str] = None
) -> None:
    global _ua_manager_instance
    if _ua_manager_instance is not None:
        raise RuntimeError("UserAgentManager is already initialized. Set config before first use.")
    
    global _ua_manager_config
    _ua_manager_config["redownload"] = redownload
    _ua_manager_config["max_age_days"] = max_age_days
    _ua_manager_config["cache_path"] = cache_path

# This is a helper function to get the UserAgentManager instance.
def get_user_agent_manager() -> UserAgentManager:
    global _ua_manager_instance, _ua_manager_config
    if _ua_manager_instance is None:
        _ua_manager_instance = UserAgentManager(redownload=_ua_manager_config["redownload"], max_age_days=_ua_manager_config["max_age_days"], cache_path=_ua_manager_config["cache_path"])
        _ua_manager_instance.add_source("microlink", _microlink_source)  # <-- default source here
    return _ua_manager_instance

# This is a helper function to reset the UserAgentManager instance.
def reset_user_agent_manager() -> None:
    global _ua_manager_instance, _ua_manager_config
    _ua_manager_instance = None
    _ua_manager_config = {
        "redownload": "lazy",
        "max_age_days": 7,
        "cache_path": None
    }

# This is a helper function to add a new source to the UserAgentManager instance.
def add_user_agent_source(name: str, fetch_fn: Callable[[], List[str]]) -> None:
    get_user_agent_manager().add_source(name, fetch_fn)

# This is a helper function to initialize the UserAgentManager instance.
def init_user_agents() -> None:
    get_user_agent_manager().initialize()

# This is a helper function to get a random user agent from the UserAgentManager instance.
def get_random_user_agent() -> Optional[str]:
    return get_user_agent_manager().get_random()

# This is a helper function to get all user agents from the UserAgentManager instance.
def get_all_user_agents() -> List[str]:
    return get_user_agent_manager().get_all()
