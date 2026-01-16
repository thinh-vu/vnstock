# Lazy initialization to avoid circular import deadlock
_initialized = False

def _ensure_initialized():
    """Ensure vnstock environment is initialized (called on first use)."""
    global _initialized
    if _initialized:
        return
    
    try:
        from vnstock.core.utils.env import id_valid
        id_valid()
        _initialized = True
    except Exception as e:
        # Silently ignore errors to avoid blocking imports
        _initialized = True  # Mark as initialized to avoid retry loops