from typing import Optional
import inspect
from abc import ABC
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_exponential
from vnstock.config import Config
from vnstock.core.registry import ProviderRegistry


def dynamic_method(func):
    """
    Decorator for adapter methods:
    - Ensures the loaded provider supports this method
    - Filters kwargs to only those the provider’s signature accepts
    """
    method_name = func.__name__

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self._provider, method_name):
            raise NotImplementedError(
                f"Source '{self.source}' does not support '{method_name}'"
            )
        provider_method = getattr(self._provider, method_name)
        sig = inspect.signature(provider_method)
        filtered = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return provider_method(*args, **filtered)

    return wrapper


class BaseAdapter(ABC):
    """
    Base adapter that uses ProviderRegistry to discover and instantiate
    providers from both explorer and connector packages.
    """

    _module_name: str  # e.g. "quote", "company", etc.

    def __init__(
        self,
        source: str,
        symbol: Optional[str] = None,
        **kwargs
    ):
        # Preserve original for error messages
        self.source = source
        self.symbol = symbol

        # Get provider class from registry
        try:
            impl_cls = ProviderRegistry.get(self._module_name, source)
        except ValueError as e:
            raise ValueError(str(e)) from e

        # Inspect constructor signature and filter kwargs
        sig = inspect.signature(impl_cls.__init__)
        init_kwargs = {}
        # Only pass symbol if accepted
        if symbol is not None and 'symbol' in sig.parameters:
            init_kwargs['symbol'] = symbol
        # Pass only recognized provider kwargs
        for key, val in kwargs.items():
            if key in sig.parameters:
                init_kwargs[key] = val

        # Instantiate the provider
        self._provider = impl_cls(**init_kwargs)

    def __getattr__(self, name):
        # Delegate attribute access to the provider
        return getattr(self._provider, name)

    @retry(
        stop=stop_after_attempt(Config.RETRIES),
        wait=wait_exponential(
            multiplier=Config.BACKOFF_MULTIPLIER,
            min=Config.BACKOFF_MIN,
            max=Config.BACKOFF_MAX
        )
    )
    def history(self, *args, **kwargs):
        # Generic retry wrapper for any .history() calls
        return self._provider.history(*args, **kwargs)
