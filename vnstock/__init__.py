"""
vnstock: fetch and standardise Vietnamese stock market data.

This is the free package. Extended features (derivatives price board, longer
financial statement history, odd-lot prices...) live in `vnstock_data`, the sponsor
package, which mirrors the classes and arguments here: switching
`from vnstock import ...` to `from vnstock_data import ...` is enough. Registering an
API key does not unlock those features in this package.

Guide for AI coding assistants (optional, OFF by default)
---------------------------------------------------------
vnstock can write a short reference block on how to use the library into an AI
assistant's instruction file: the project's `AGENTS.md`, plus the global files of
Claude Code, Codex or Antigravity only when named explicitly. Nothing is written on
import. The block's text ships inside the `vnai` package; it is not downloaded.

    import vnstock
    vnstock.enable_agent()             # opt in, project AGENTS.md only
    vnstock.setup_agent()              # write it now
    vnstock.agent_status()             # what would be written, and where
    vnstock.disable_agent()            # opt out
    vnstock.remove_agent_files("all")  # remove blocks, including ones older versions left
"""

try:
    from vnstock.core.utils.env import check_sponsor_package

    check_sponsor_package()
except Exception:
    pass


import vnai

# Lazy import Vnstock to avoid circular import deadlock
_Vnstock = None


def _get_vnstock():
    """Lazy load Vnstock class."""
    global _Vnstock
    if _Vnstock is None:
        from vnstock.common.client import Vnstock as _VnstockClass

        _Vnstock = _VnstockClass
    return _Vnstock


# Create a lazy proxy for Vnstock
class Vnstock:
    """Lazy proxy for vnstock.common.client.Vnstock to avoid circular import."""

    def __new__(cls, *args, **kwargs):
        actual_class = _get_vnstock()
        return actual_class(*args, **kwargs)


# Use standard vnstock classes
# Load UI and helper classes
from vnstock.ui import (  # noqa: E402
    Broker,
    Fundamental,
    Market,
    Reference,
    Retail,
    show_api,
    show_doc,
)

from .api.company import Company  # noqa: E402
from .api.financial import Finance  # noqa: E402
from .api.listing import Listing  # noqa: E402
from .api.quote import Quote  # noqa: E402
from .api.trading import Trading  # noqa: E402
from .explorer.fmarket import Fund  # noqa: E402

show_docs = show_doc  # Alias for better parity


# Market constants
# Load connector modules to register providers
from . import connector  # noqa: E402
from .constants import (  # noqa: E402
    EXCHANGES,
    INDEX_GROUPS,
    INDICES_INFO,
    INDICES_MAP,
    SECTOR_IDS,
)

# User authentication and API key registration
from .core.utils.auth import (  # noqa: E402
    change_api_key,
    check_status,
    register_user,
)

# Load explorer modules to register providers (lazy to avoid deadlock)
_explorer_modules_loaded = False


def _ensure_explorer_modules_loaded():
    """Lazy load explorer modules to avoid circular import deadlock."""
    global _explorer_modules_loaded
    if _explorer_modules_loaded:
        return
    try:
        from .explorer import kbs, msn, vci  # noqa: F401

        _explorer_modules_loaded = True
    except Exception as e:
        _explorer_modules_loaded = True  # Mark as loaded to avoid retry loops
        import warnings

        warnings.warn(f"Failed to load explorer modules: {e}", stacklevel=2)


__all__ = [
    "Vnstock",
    "Quote",
    "Listing",
    "Company",
    "Finance",
    "Trading",
    "Fund",
    "ui",
    "show_api",
    "show_doc",
    "Reference",
    "Market",
    "Fundamental",
    "Retail",
    "Broker",
    "connector",
    "INDICES_INFO",
    "INDICES_MAP",
    "INDEX_GROUPS",
    "SECTOR_IDS",
    "EXCHANGES",
    # Authentication
    "register_user",
    "change_api_key",
    "check_status",
    # Agent Environment
    "setup_agent",
    "agent_status",
    "disable_agent",
    "enable_agent",
    "remove_agent_files",
]

# Delay vnai.setup() to avoid circular import deadlock
_vnai_initialized = False


def _ensure_vnai_initialized():
    """Ensure vnai is initialized (called on first use)."""
    global _vnai_initialized
    if _vnai_initialized:
        return
    try:
        vnai.setup()
        _vnai_initialized = True
    except Exception:
        _vnai_initialized = True  # Mark as initialized to avoid retry loops


# Lazy check for dependency compatibility (non-blocking, compact output)
try:
    from vnstock.core.utils.upgrade import update_notice

    update_notice(verbose=False)
except Exception:
    # Silently fail if notice check has any issues
    pass


def setup_agent(async_mode: bool = False) -> bool:
    """
    Write the AI assistant guide into the targets enabled with `enable_agent()`.

    Does nothing until you opt in. Enabled without naming targets, it writes only
    `AGENTS.md` in the current directory. Preview with `agent_status()`.
    """
    try:
        from vnstock.core.utils.agents import init_agent_environment

        return init_agent_environment(async_mode=async_mode)
    except Exception:
        return False


def agent_status(project_root: str = "."):
    """Show what the agent bootstrap would write, where, and why."""
    from vnstock.core.utils.agents import agent_status as _status

    return _status(project_root)


def disable_agent(*targets: str):
    """
    Opt out of the AI assistant guide and persist the choice.

    `disable_agent()` turns it off entirely; `disable_agent("global")` only the
    machine-wide files. Blocks already written stay until `remove_agent_files()`.
    """
    from vnstock.core.utils.agents import disable_agent as _disable

    return _disable(*targets)


def enable_agent(*targets: str):
    """
    Opt in to the AI assistant guide and persist the choice.

    Without targets, only the project's `AGENTS.md`. Global files must be named:
    `enable_agent("claude")`, `"codex"`, `"antigravity"`, or `"global"` for all three.
    Nothing is written until `setup_agent()` is called.
    """
    from vnstock.core.utils.agents import enable_agent as _enable

    return _enable(*targets)


def remove_agent_files(*targets: str):
    """
    Remove the vnstock block from rules files already written.

    Files that held nothing else are deleted; the user's own content is kept.
    Pair this with `disable_agent()`, otherwise the next `setup_agent()` writes them again.

    Group names: "global" for the three machine-wide files, "legacy" for the
    paths versions before 2.6.0 wrote to and this one no longer touches, "all"
    for everything.
    """
    from vnstock.core.utils.agents import remove_agent_files as _remove

    return _remove(*targets)


# Import no longer calls setup_agent() (removed in 4.0.9). Earlier versions wrote into
# AI assistants' instruction files on every `import vnstock`, including global files
# read in every project on the machine, with text downloaded from vnstocks.com, and
# nobody had asked for it. A developer in the community rightly called that prompt
# injection (09/2026). What remains on import is a one-time, read-only notice when an
# older version left such a block behind, so the user can remove it.
#
# The hook is only safe from vnai 2.6.2, where it never writes; 2.6.1 and earlier
# write from the same entry point, hence the feature check.
try:
    from vnai.beam.agent_bootstrap import BOOTSTRAP_VERSION as _  # noqa: F401
    from vnai import async_setup_agent_environment as _leftover_notice

    _leftover_notice()
except Exception:
    pass
