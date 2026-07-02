from __future__ import annotations

from typing import Any

import pandas as pd


def _is_rate_limit(exc: Exception) -> bool:
    """Return True if *exc* looks like an HTTP 429 / rate-limit error."""
    msg = " ".join(str(a) for a in exc.args).lower()
    return "429" in msg or "rate limit" in msg or "too many requests" in msg


class BaseUI:
    """Base class for all UI modules."""

    def _dispatch(self, domain_name: str, method_name: str, *args, **kwargs) -> Any:
        """
        Dispatch the message to native providers/connectors.
        Automatically rotates providers via the load-balancer router when a
        POOLS entry exists and the caller did not explicitly pass source=.
        """
        from vnstock.ui._registry import MAP

        if domain_name not in MAP or method_name not in MAP[domain_name]:
            raise AttributeError(
                f"Method '{method_name}' not implemented for domain '{domain_name}'"
            )

        meta = MAP[domain_name][method_name]

        # 1. Handle nested sub-domains (e.g., Market -> equity -> ohlcv)
        consumed_subdomain: str | None = None
        if isinstance(meta, dict) and args:
            actual_method = args[0]
            if actual_method in meta:
                consumed_subdomain = actual_method
                meta = meta[actual_method]
                args = args[1:]
            else:
                raise AttributeError(
                    f"Method '{actual_method}' not found in sub-domain "
                    f"'{method_name}' of '{domain_name}'"
                )

        # 2. Handle redirection tuples (length 2)
        if isinstance(meta, tuple) and len(meta) == 2:
            redirect_domain, redirect_method = meta
            return self._dispatch(redirect_domain, redirect_method, *args, **kwargs)

        # 3. Standard Metadata Unpack
        try:
            module_type = meta[0]
            sub_module = meta[1]
            class_name = meta[2]
            function_name = meta[3]
        except (IndexError, TypeError) as e:
            raise AttributeError(
                f"Invalid registry entry for '{domain_name}.{method_name}'. Got: {meta}"
            ) from e

        # Record whether the caller explicitly passed source= BEFORE we apply the MAP default.
        _caller_set_source: bool = "source" in kwargs and kwargs["source"] is not None

        # Apply MAP default source when caller did not provide one.
        if len(meta) > 4 and not _caller_set_source:
            kwargs["source"] = meta[4]

        # 3b. Pop cache control kwargs before they leak into provider calls.
        _use_cache = kwargs.pop("use_cache", None)
        _cache_ttl = kwargs.pop("cache_ttl", None)

        # 3c. Load-balancer: override source via router when caller did not specify.
        _using_router = False
        _pool_key: tuple | None = None
        _pool_providers: list[str] = []

        if not _caller_set_source:
            from vnstock.core.router import router
            from vnstock.ui._pools import POOLS, _build_pool_key

            _pool_key = _build_pool_key(domain_name, method_name, consumed_subdomain)
            if _pool_key in POOLS:
                _pool_providers = POOLS[_pool_key]
                kwargs["source"] = router.pick(_pool_key, _pool_providers)
                _using_router = True

        # 3d. Cache lookup (skip when use_cache=False).
        _cache_manager = None
        _cache_key: str | None = None
        if _use_cache is not False:
            try:
                from vnstock.core.cache import get_cache_manager, make_cache_key

                _cache_manager = get_cache_manager()
                if _cache_manager.config.enabled:
                    _cache_key = make_cache_key(
                        kwargs.get("source", ""),
                        function_name,
                        {
                            "symbol": getattr(self, "symbol", None),
                            "args": list(args),
                            **{
                                k: v
                                for k, v in kwargs.items()
                                if k not in ("source", "random_agent", "show_log")
                            },
                        },
                    )
                    _cached = _cache_manager.get(_cache_key)
                    if _cached is not None:
                        return _cached
            except Exception:
                # Cache errors must never break normal operation
                _cache_manager = None
                _cache_key = None

        # 4. Multi-symbol Handling (Universal)
        symbol = getattr(self, "symbol", None)
        if isinstance(symbol, list) and module_type == "api":
            all_results = []
            for s in symbol:
                temp_inst = type(self)(symbol=s)
                res = temp_inst._dispatch(domain_name, method_name, *args, **kwargs)
                all_results.append(res)
            if all_results and isinstance(all_results[0], pd.DataFrame):
                return pd.concat(all_results).reset_index(drop=True)
            return all_results

        # 5. Native dispatch (with retry loop when router is active)
        max_attempts = len(_pool_providers) if _using_router and _pool_providers else 1
        last_exc: Exception | None = None

        for attempt in range(max_attempts):
            try:
                result = self._execute_dispatch(
                    module_type,
                    sub_module,
                    class_name,
                    function_name,
                    symbol,
                    args,
                    kwargs,
                )
                if _using_router and isinstance(result, pd.DataFrame):
                    result.attrs["source_used"] = kwargs.get("source", "")

                # Write to cache on success (skip when use_cache=False).
                if (
                    _use_cache is not False
                    and _cache_manager is not None
                    and _cache_key is not None
                ):
                    try:
                        ttl = (
                            _cache_ttl
                            if isinstance(_cache_ttl, int)
                            else _cache_manager.config.ttl
                        )
                        _cache_manager.set(_cache_key, result, ttl)
                    except Exception:
                        pass  # cache write errors must never break the response

                return result

            except Exception as exc:
                retriable = _is_retriable(exc)
                if _using_router and retriable and _pool_key and _pool_providers:
                    from vnstock.core.router import router
                    from vnstock.ui._pools import POOLS

                    router.mark_failed(_pool_key, kwargs["source"], _is_rate_limit(exc))
                    if attempt < max_attempts - 1:
                        kwargs["source"] = router.pick(_pool_key, _pool_providers)
                        last_exc = exc
                        continue
                raise

        if last_exc is not None:
            raise last_exc  # type: ignore[misc]

        # Should never reach here
        raise AttributeError(
            f"Method '{method_name}' not implemented for domain '{domain_name}'"
        )

    def _execute_dispatch(
        self,
        module_type: str,
        sub_module: str,
        class_name: str | None,
        function_name: str,
        symbol: Any,
        args: tuple,
        kwargs: dict,
    ) -> Any:
        """Instantiate the provider class and invoke the target function."""
        import importlib
        import inspect

        if module_type == "api":
            module = importlib.import_module(f"vnstock.{sub_module}")
            if class_name:
                cls = getattr(module, class_name)
                sig = inspect.signature(cls.__init__)

                init_kwargs: dict = {}
                for param in [
                    "symbol",
                    "symbol_id",
                    "source",
                    "random_agent",
                    "show_log",
                ]:
                    if param in sig.parameters:
                        if param in ["symbol", "symbol_id"]:
                            init_kwargs[param] = symbol
                        elif param in kwargs:
                            init_kwargs[param] = kwargs.pop(param)

                obj = cls(**init_kwargs)
                func = getattr(obj, function_name)

                func_sig = inspect.signature(func)
                has_kwargs = any(
                    p.kind == p.VAR_KEYWORD for p in func_sig.parameters.values()
                )
                clean_kwargs = {
                    k: v
                    for k, v in kwargs.items()
                    if k not in ["source", "random_agent", "show_log"]
                }
                if not has_kwargs:
                    clean_kwargs = {
                        k: v
                        for k, v in clean_kwargs.items()
                        if k in func_sig.parameters
                    }

                if symbol:
                    consumed_by_init = "symbol" in sig.parameters
                    in_kwargs = any(
                        k in clean_kwargs
                        for k in ["symbol", "group", "code", "ticker", "query"]
                    )
                    if not consumed_by_init and not in_kwargs and not args:
                        if "symbol" in func_sig.parameters or has_kwargs:
                            return func(symbol, *args, **clean_kwargs)

                return func(*args, **clean_kwargs)

            else:
                func = getattr(module, function_name)
                func_sig = inspect.signature(func)
                has_kwargs = any(
                    p.kind == p.VAR_KEYWORD for p in func_sig.parameters.values()
                )
                clean_kwargs = {
                    k: v
                    for k, v in kwargs.items()
                    if k not in ["source", "random_agent", "show_log"]
                }
                if not has_kwargs:
                    clean_kwargs = {
                        k: v
                        for k, v in clean_kwargs.items()
                        if k in func_sig.parameters
                    }
                return func(*args, **clean_kwargs)

        elif module_type == "explorer":
            module = importlib.import_module(f"vnstock.explorer.{sub_module}")
            if class_name:
                cls = getattr(module, class_name)
                try:
                    sig = inspect.signature(cls.__init__)
                    init_kwargs = {}
                    for param in ["symbol", "symbol_id", "random_agent", "show_log"]:
                        if param in sig.parameters:
                            if param in ["symbol", "symbol_id"]:
                                init_kwargs[param] = symbol
                            elif param in kwargs:
                                init_kwargs[param] = kwargs.pop(param)
                    obj = cls(**init_kwargs)
                except (ValueError, TypeError):
                    obj = cls()
                func = getattr(obj, function_name)
            else:
                func = getattr(module, function_name)

            func_sig = inspect.signature(func)
            has_kwargs = any(
                p.kind == p.VAR_KEYWORD for p in func_sig.parameters.values()
            )
            clean_kwargs = {
                k: v
                for k, v in kwargs.items()
                if k not in ["source", "random_agent", "show_log"]
            }
            if not has_kwargs:
                clean_kwargs = {
                    k: v for k, v in clean_kwargs.items() if k in func_sig.parameters
                }
            return func(*args, **clean_kwargs)

        elif module_type == "connector":
            module = importlib.import_module(f"vnstock.connector.{sub_module}")
            cls = getattr(module, class_name)
            obj = cls()
            return getattr(obj, function_name)(*args, **kwargs)

        raise AttributeError(f"Unknown module_type '{module_type}'")


def _is_retriable(exc: Exception) -> bool:
    """Return True if *exc* is a transient error worth retrying."""
    try:
        import requests

        if isinstance(
            exc,
            (requests.exceptions.Timeout, requests.exceptions.ConnectionError),
        ):
            return True
    except ImportError:
        pass

    if isinstance(exc, (ValueError, RuntimeError)):
        msg = str(exc).lower()
        return any(
            m in msg
            for m in ("429", "rate limit", "too many requests", "503", "502", "500")
        )
    return False


class BaseDetailUI(BaseUI):
    """Base class for detail UI modules (e.g. Reference().company('VNM'))"""

    def __init__(self, symbol: str = None, **kwargs):
        self.symbol = symbol
        self.params = kwargs
