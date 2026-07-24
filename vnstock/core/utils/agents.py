# vnstock/core/utils/agents.py

"""
Thin wrapper for AI Agent skills and environment management.
The actual implementation is safely encapsulated in the `vnai` tier package.
NOT part of the public vnstock API. Do not add to __init__.py exports.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def load_skill_catalog() -> Optional[Dict[str, Any]]:
    """
    Fetch the catalog of all available AI skills.
    Requires vnai tier to be installed.
    """
    try:
        from vnai import load_skill_catalog as _load_catalog

        return _load_catalog()
    except ImportError:
        logger.warning(
            "Tính năng này yêu cầu gói 'vnai'. "
            "Vui lòng cài đặt bằng lệnh: pip install -U vnai"
        )
        return None
    except Exception as e:
        logger.error(f"Lỗi khi tải danh mục skill: {e}")
        return None


def load_skill(name: str, component: str = "content") -> Optional[str]:
    """
    Load protected skill content for in-session use.
    Requires vnai tier to be installed.

    Args:
        name: Skill slug (e.g., "market-analyzer")
        component: "content", "config", "script:<filename>", "reference:<filename>"
    """
    try:
        from vnai import load_skill as _load_skill

        return _load_skill(name, component)
    except ImportError:
        logger.warning(
            "Tính năng này yêu cầu gói 'vnai'. "
            "Vui lòng cài đặt bằng lệnh: pip install -U vnai"
        )
        return None
    except Exception as e:
        logger.error(f"Lỗi khi tải skill '{name}': {e}")
        return None


def clear_cache() -> None:
    """Clear in-memory skill cache."""
    try:
        from vnai import clear_skill_cache

        clear_skill_cache()
    except ImportError:
        pass


def list_cached() -> list:
    """List currently cached skill components."""
    try:
        from vnai import list_cached_skills

        return list_cached_skills()
    except ImportError:
        return []


def init_agent_environment(project_root: str = ".", async_mode: bool = True) -> bool:
    """
    Initialize or update the .agents/AGENTS.md file in the user's project root
    with the vnstock Dynamic Skill Router instructions.

    This feature requires the 'vnai' tier to be installed.

    Args:
        project_root: The root directory of the user's project. Default is current dir.
        async_mode: If True, runs the initialization in a background thread.

    Returns:
        bool: True if successfully started or completed, False otherwise.
    """
    try:
        if async_mode:
            from vnai import async_setup_agent_environment

            async_setup_agent_environment(project_root)
            return True
        else:
            from vnai import setup_agent_environment

            return setup_agent_environment(project_root)
    except ImportError:
        # Silently fail if vnai is not present during library init, to avoid spamming users
        return False
    except Exception as e:
        logger.error(f"Lỗi khi cấu hình agent environment: {e}")
        return False
