import inspect
import importlib
import pkgutil
from abc import ABC
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_exponential
from vnstock.config import Config


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
    Base adapter that dynamically discovers the correct explorer subpackage,
    imports the provider's module, and instantiates its class with only
    the acceptable constructor parameters.
    """

    _module_name: str  # e.g. "quote", "company", etc.

    def __init__(self, source: str, symbol: str = None, **kwargs):
        # Preserve original for error messages
        self.source = source
        self.symbol = symbol

        # Discover all subpackages under vnstock.explorer
        import vnstock.explorer as expkg
        available = {info.name for info in pkgutil.iter_modules(expkg.__path__)}
        # Case-insensitive match of requested source
        matches = {name for name in available if name.lower() == source.lower()}
        if not matches:
            raise ValueError(
                f"No data-source '{source}' found. Available: {sorted(available)}"
            )
        real_source = matches.pop()

        # Build module path and import
        module_path = f"{expkg.__name__}.{real_source}.{self._module_name}"
        try:
            mod = importlib.import_module(module_path)
        except ImportError as e:
            raise ValueError(
                f"Source '{real_source}' does not provide '{self._module_name}.'"
            ) from e

        # Get the implementation class
        try:
            impl_cls = getattr(mod, self.__class__.__name__)
        except AttributeError as e:
            raise ValueError(
                f"Module '{module_path}' has no class '{self.__class__.__name__}'"
            ) from e

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
