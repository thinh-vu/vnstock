# vnstock/core/utils/agents.py

"""
Thin wrapper over `vnai` for the AI assistant guide and topic guides ("skills").

The implementation lives in `vnai`. Since vnai 2.6.2 the guide is opt-in, is never
written on import, and its text ships inside the package instead of being downloaded.
Topic guides are downloaded only when `load_skill()` is called, with the API key in
the Authorization header.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_INSTALL_HINT = (
    "Tính năng này yêu cầu gói 'vnai'. Cài bằng lệnh: "
    "python -m pip install -U --extra-index-url https://vnstocks.com/api/simple vnai"
)


def load_skill_catalog() -> Optional[Dict[str, Any]]:
    """
    Fetch the catalog of all available AI skills.
    Requires vnai tier to be installed.
    """
    try:
        from vnai import load_skill_catalog as _load_catalog

        return _load_catalog()
    except ImportError:
        logger.warning(_INSTALL_HINT)
        return None
    except Exception as e:
        logger.error(f"Lỗi khi tải danh mục skill: {e}")
        return None


def load_skill(name: str, component: str = "content") -> Optional[str]:
    """
    Download one topic guide from vnstocks.com and return its text.

    The text is reference documentation for the current session. Markdown content
    starts with a line saying where it came from, so an AI assistant reading it can
    tell it apart from the user's own request.

    Args:
        name: Skill slug (e.g., "market-analyzer")
        component: "content", "config", "script:<filename>", "reference:<filename>"
    """
    try:
        from vnai import load_skill as _load_skill

        return _load_skill(name, component)
    except ImportError:
        logger.warning(_INSTALL_HINT)
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


_UPGRADE_HINT = (
    "Tính năng này yêu cầu vnai >= 2.6.2. Cập nhật bằng lệnh: "
    "python -m pip install -U --extra-index-url https://vnstocks.com/api/simple vnai"
)


def init_agent_environment(project_root: str = ".", async_mode: bool = True) -> bool:
    """
    Write the AI assistant guide into the targets the user has enabled.

    Nothing is written until the user opts in with `enable_agent()` (or the
    `VNSTOCK_AGENT_TARGETS` environment variable). Enabled without naming targets,
    only `AGENTS.md` in `project_root` is written; the machine-wide files of Claude
    Code, Codex and Antigravity must each be enabled by name.

    Args:
        project_root: The root directory of the user's project. Default is current dir.
        async_mode: Kept for backward compatibility and ignored: writing a user's
            files from a background thread made the result unpredictable (two writers
            once left duplicate blocks), so the write always runs in the caller.

    Returns:
        bool: True if at least one target was written or already up to date.
    """
    try:
        from vnai.beam.agent_bootstrap import BOOTSTRAP_VERSION  # noqa: F401  (vnai >= 2.6.2)
        from vnai import setup_agent_environment
    except ImportError:
        logger.warning(_UPGRADE_HINT)
        return False
    try:
        return setup_agent_environment(project_root)
    except Exception as e:
        logger.error(f"Lỗi khi cấu hình agent environment: {e}")
        return False


def agent_status(project_root: str = ".") -> Optional[Dict[str, Any]]:
    """
    Report what the agent bootstrap would write and why.

    Returns a dict with the resolved per-target decision, the path of each rules
    file, whether it already exists, the config file location and any environment
    variable currently overriding the configuration.
    """
    try:
        from vnai import agent_status as _status

        return _status(project_root)
    except ImportError:
        logger.warning(_UPGRADE_HINT)
        return None


def disable_agent(*targets: str) -> Optional[Dict[str, Any]]:
    """
    Turn the agent bootstrap off and remember the choice.

    No arguments disables it entirely. Pass `"global"` to keep only the project's
    own `AGENTS.md`, or individual target names (`"antigravity"`, `"claude"`,
    `"codex"`, `"project"`).

    The choice is stored in `~/.vnstock/config/agent.json` and survives restarts.
    """
    try:
        from vnai import disable_agent_setup

        return disable_agent_setup(*targets)
    except ImportError:
        logger.warning(_UPGRADE_HINT)
        return None


def enable_agent(*targets: str) -> Optional[Dict[str, Any]]:
    """Re-enable the agent bootstrap, entirely or for the named targets."""
    try:
        from vnai import enable_agent_setup

        return enable_agent_setup(*targets)
    except ImportError:
        logger.warning(_UPGRADE_HINT)
        return None


def remove_agent_files(*targets: str) -> Optional[Dict[str, str]]:
    """
    Take the vnstock block back out of the rules files it was written into.

    Files that held nothing else are deleted; files the user also wrote in keep
    their own content. No arguments means the active targets; `"global"` leaves
    the project's `AGENTS.md` alone, `"legacy"` cleans up the paths versions
    before 2.6.0 wrote to (Cursor, Windsurf, Cline, Copilot, `~/.clauderc`,
    `~/.gemini/config/AGENTS.md`, `~/AGENTS.md`), and `"all"` does both.

    Disabling and removing are separate steps - call `disable_agent()` too, or
    the next import writes the files again.
    """
    try:
        from vnai import remove_agent_files as _remove

        return _remove(*targets)
    except ImportError:
        logger.warning(_UPGRADE_HINT)
        return None
