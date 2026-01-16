"""
Deprecation utilities for vnstock.

Provides decorators and utilities to mark and handle deprecated features,
similar to pandas deprecation warnings.
"""

import warnings
import functools
from typing import Optional, Callable, Any, Type
from datetime import datetime

from vnstock.core.exceptions import DeprecationWarning as VnstockDeprecationWarning


class DeprecationRegistry:
    """
    Registry to track and manage deprecated features in vnstock.
    
    This allows centralized management of deprecation notices and version tracking.
    """
    
    _registry = {}
    
    @classmethod
    def register(
        cls,
        name: str,
        version: str,
        removal_version: Optional[str] = None,
        alternative: Optional[str] = None,
        reason: Optional[str] = None
    ):
        """
        Register a deprecated feature.
        
        Args:
            name: Name of the deprecated feature (e.g., 'TCBS', 'function_name')
            version: Version when deprecation started
            removal_version: Version when feature will be removed
            alternative: Recommended alternative to use
            reason: Reason for deprecation
        """
        cls._registry[name] = {
            'version': version,
            'removal_version': removal_version,
            'alternative': alternative,
            'reason': reason,
            'registered_at': datetime.now()
        }
    
    @classmethod
    def get(cls, name: str) -> Optional[dict]:
        """Get deprecation info for a feature."""
        return cls._registry.get(name)
    
    @classmethod
    def list_all(cls) -> dict:
        """List all deprecated features."""
        return cls._registry.copy()


def deprecated(
    version: str,
    removal_version: Optional[str] = None,
    alternative: Optional[str] = None,
    reason: Optional[str] = None,
    stacklevel: int = 2
):
    """
    Decorator to mark functions/methods as deprecated.
    
    Similar to pandas.util._decorators.deprecate_nonkeyword_arguments
    
    Args:
        version: Version when deprecation started
        removal_version: Version when feature will be removed
        alternative: Recommended alternative to use
        reason: Reason for deprecation
        stacklevel: Stack level for warning (default 2 for direct caller)
        
    Returns:
        Decorated function that issues deprecation warning
        
    Examples:
        >>> @deprecated(version='3.4.0', removal_version='3.5.0', 
        ...             alternative='use new_function instead')
        ... def old_function():
        ...     pass
    """
    def decorator(func: Callable) -> Callable:
        # Register the deprecation
        DeprecationRegistry.register(
            name=func.__qualname__,
            version=version,
            removal_version=removal_version,
            alternative=alternative,
            reason=reason
        )
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            msg = f"'{func.__qualname__}' is deprecated"
            
            if version:
                msg += f" since version {version}"
            
            if removal_version:
                msg += f" and will be removed in version {removal_version}"
            
            if alternative:
                msg += f". Use '{alternative}' instead"
            
            if reason:
                msg += f". Reason: {reason}"
            
            msg += "."
            
            warnings.warn(
                msg,
                category=VnstockDeprecationWarning,
                stacklevel=stacklevel + 1
            )
            
            return func(*args, **kwargs)
        
        # Mark the wrapper as deprecated
        wrapper.__deprecated__ = True
        wrapper.__deprecation_version__ = version
        wrapper.__removal_version__ = removal_version
        wrapper.__alternative__ = alternative
        
        return wrapper
    
    return decorator


def deprecate_provider(
    provider_name: str,
    version: str,
    removal_version: Optional[str] = None,
    alternative: Optional[str] = None,
    reason: Optional[str] = None
):
    """
    Decorator to mark data providers as deprecated.
    
    Args:
        provider_name: Name of the provider (e.g., 'TCBS', 'VCI')
        version: Version when deprecation started
        removal_version: Version when provider will be removed
        alternative: Recommended alternative provider
        reason: Reason for deprecation
        
    Returns:
        Decorated class that issues deprecation warning on instantiation
        
    Examples:
        >>> @deprecate_provider(
        ...     provider_name='TCBS',
        ...     version='3.4.0',
        ...     removal_version='3.5.0',
        ...     alternative='VCI',
        ...     reason='TCBS API is no longer publicly accessible'
        ... )
        ... class TCBSQuote:
        ...     pass
    """
    def decorator(cls: Type) -> Type:
        # Register the deprecation
        DeprecationRegistry.register(
            name=f"Provider:{provider_name}",
            version=version,
            removal_version=removal_version,
            alternative=alternative,
            reason=reason
        )
        
        original_init = cls.__init__
        
        @functools.wraps(original_init)
        def new_init(self, *args, **kwargs):
            msg = f"Provider '{provider_name}' is deprecated"
            
            if version:
                msg += f" since version {version}"
            
            if removal_version:
                msg += f" and will be removed in version {removal_version}"
            
            if alternative:
                msg += f". Use '{alternative}' provider instead"
            
            if reason:
                msg += f". Reason: {reason}"
            
            msg += "."
            
            warnings.warn(
                msg,
                category=VnstockDeprecationWarning,
                stacklevel=2
            )
            
            original_init(self, *args, **kwargs)
        
        cls.__init__ = new_init
        cls.__deprecated__ = True
        cls.__deprecation_version__ = version
        cls.__removal_version__ = removal_version
        cls.__alternative__ = alternative
        
        return cls
    
    return decorator


def warn_deprecated(
    message: str,
    version: Optional[str] = None,
    removal_version: Optional[str] = None,
    stacklevel: int = 2
):
    """
    Issue a deprecation warning with custom message.
    
    Args:
        message: Custom deprecation message
        version: Version when deprecation started
        removal_version: Version when feature will be removed
        stacklevel: Stack level for warning
        
    Examples:
        >>> warn_deprecated(
        ...     "TCBS source is deprecated",
        ...     version='3.4.0',
        ...     removal_version='3.5.0'
        ... )
    """
    full_msg = message
    
    if version:
        full_msg += f" (deprecated since {version}"
        if removal_version:
            full_msg += f", will be removed in {removal_version}"
        full_msg += ")"
    
    warnings.warn(
        full_msg,
        category=VnstockDeprecationWarning,
        stacklevel=stacklevel + 1
    )


def get_deprecation_info(name: str) -> Optional[dict]:
    """
    Get deprecation information for a feature.
    
    Args:
        name: Name of the feature
        
    Returns:
        Dictionary with deprecation info or None
    """
    return DeprecationRegistry.get(name)


def list_deprecated_features() -> dict:
    """
    List all deprecated features in vnstock.
    
    Returns:
        Dictionary of all deprecated features with their info
    """
    return DeprecationRegistry.list_all()
