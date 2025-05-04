import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Callable, List, Optional
from vnstock.core.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 Chrome/110.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 Version/16.1 Mobile Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

# This is the main class for managing user agents.
class UserAgentManager:
    def __init__(self, redownload: str = "lazy", max_age_days: int = 7, cache_path: Optional[str] = None) -> None:
        self.initialized = False
        self.redownload = redownload  # 'force', 'lazy', or 'no'
        self.max_age_days = max_age_days
        self.sources: dict[str, Callable[[], List[str]]] = {}
        self.user_agents: List[str] = []
        self.cache_path = Path(cache_path or ".cache/user_agents_combined.json")
        self.cache_path.parent.mkdir(exist_ok=True)
    
    # This is a helper function to add a new source to the UserAgentManager instance.
    def add_source(self, name: str, fetch_function: Callable[[], List[str]]) -> None:
        self.sources[name] = fetch_function

    # This is a helper function to check if the cache is expired.
    def _is_cache_expired(self) -> bool:
        if not self.cache_path.exists():
            return True
        modified_time = datetime.fromtimestamp(self.cache_path.stat().st_mtime)
        return datetime.now() - modified_time > timedelta(days=self.max_age_days)

    # This is a helper function to load the cache.
    def _load_cache(self) -> bool:
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    self.user_agents = json.load(f)
                    return True
            except Exception as e:
                logger.error(f"[UserAgentManager] Failed to load cache: {e}")
        return False

    # This is a helper function to save the cache.
    def _save_cache(self) -> None:
        try:
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self.user_agents, f, indent=2)
        except Exception as e:
            logger.error(f"[UserAgentManager] Failed to save cache: {e}")

    # This is a helper function to merge the sources.
    def _merge_sources(self) -> List[str]:
        all_agents = []
        for name, fetch_fn in self.sources.items():
            try:
                agents = fetch_fn()
                all_agents.extend(agents)
                logger.info(f"[{name}] fetched {len(agents)} user-agents.")
            except Exception as e:
                logger.error(f"[{name}] failed to fetch user agents: {e}")
        return list(set(all_agents))  # deduplicate

    # This is a helper function to initialize the UserAgentManager instance.
    def initialize(self) -> None:
        if self.initialized:
            return
        
        self.initialized = True
        
        if self.redownload == "no":
            if not self._load_cache():
                logger.info("[UAManager] No cache found. Switching to 'force' mode.")
                self.redownload = "force"

        if self.redownload == "lazy":
            if self._is_cache_expired():
                logger.info("[UAManager] Cache expired. Re-downloading...")
                self.redownload = "force"
            else:
                if self._load_cache():
                    return

        if self.redownload == "force":
            logger.info("[UAManager] Downloading fresh user-agents...")
            self.user_agents = self._merge_sources()
            self._save_cache()
    
    # This is a helper function to get a random user agent from the UserAgentManager instance.
    def get_random(self) -> Optional[str]:
        self.initialize()
        return random.choice(self.get_all())

    # This is a helper function to get all user agents from the UserAgentManager instance.
    def get_all(self) -> List[str]:
        self.initialize()
        if not self.user_agents:
            logger.warning("[UAManager] No user-agents found in cache or from sources. Using default fallback list.")
            return DEFAULT_UA_LIST
        return self.user_agents