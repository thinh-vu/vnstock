from typing import Any

import pandas as pd

from vnstock.ui.helper import get_sponsor_ui_class


class BaseUI:
    """Base class for all UI modules."""

    def _dispatch(self, domain_name: str, method_name: str, *args, **kwargs) -> Any:
        """
        Dispatch the message to either the sponsor package or the native core.
        """
        from vnstock.ui._registry import MAP

        if domain_name in MAP and method_name in MAP[domain_name]:
            meta = MAP[domain_name][method_name]

            # 1. Handle nested sub-domains (e.g., Reference -> equity -> list)
            if isinstance(meta, dict) and args:
                actual_method = args[0]
                if actual_method in meta:
                    meta = meta[actual_method]
                    # Update args to remove the consumed method name
                    args = args[1:]
                else:
                    raise AttributeError(
                        f"Method '{actual_method}' not found in sub-domain '{method_name}' of '{domain_name}'"
                    )

            # 2. Handle redirection tuples (length 2)
            if isinstance(meta, tuple) and len(meta) == 2:
                redirect_domain, redirect_method = meta
                return self._dispatch(redirect_domain, redirect_method, *args, **kwargs)

            # 3. Standard Metadata Unpack
            try:
                # meta can have 4 to 7 items:
                # (module_type, sub_module, class_name, function_name, [source, return_type, description])
                module_type = meta[0]
                sub_module = meta[1]
                class_name = meta[2]
                function_name = meta[3]

                # Apply default source from registry if not provided (or None) in kwargs
                if len(meta) > 4 and (kwargs.get("source") is None):
                    kwargs["source"] = meta[4]

                # return_type and description can be used for auto-documentation (show_api)
            except (IndexError, TypeError) as e:
                raise AttributeError(
                    f"Invalid registry entry for '{domain_name}.{method_name}'. Got: {meta}"
                ) from e

            # 4. Multi-symbol Handling (Universal)
            symbol = getattr(self, "symbol", None)
            if isinstance(symbol, list) and module_type == "api":
                all_results = []
                for s in symbol:
                    # Create a temporary instance for the single symbol to avoid state pollution
                    temp_inst = type(self)(symbol=s)
                    # Call _dispatch on the temporary instance
                    res = temp_inst._dispatch(domain_name, method_name, *args, **kwargs)
                    all_results.append(res)

                if all_results and isinstance(all_results[0], pd.DataFrame):
                    return pd.concat(all_results).reset_index(drop=True)
                return all_results

            # 5. Redirection check (Sponsor Package)
            layer_map = {
                "company": "reference",
                "listing": "reference",
                "fund": "reference",
                "equity_market": "market",
                "equity_fundamental": "fundamental",
                "misc": "misc",
                "dnse": "broker",
            }
            layer = layer_map.get(domain_name)
            node_cls_name = type(self).__name__

            if layer:
                sponsor_cls = get_sponsor_ui_class(layer, node_cls_name)
                if sponsor_cls and hasattr(sponsor_cls, method_name):
                    # Call sponsor method
                    if symbol:
                        inst = sponsor_cls(symbol=symbol)
                    else:
                        inst = sponsor_cls()

                    # Filter parameters NOT supported by sponsor UI methods
                    sponsor_kwargs = kwargs.copy()
                    for p in ["source", "random_agent", "show_log"]:
                        sponsor_kwargs.pop(p, None)

                    return getattr(inst, method_name)(*args, **sponsor_kwargs)

            # 6. Native Fallback
            import importlib
            # symbol is already retrieved above

            if module_type == "api":
                module = importlib.import_module(f"vnstock.{sub_module}")
                if class_name:
                    cls = getattr(module, class_name)
                    # Inspect constructor
                    import inspect

                    sig = inspect.signature(cls.__init__)

                    # Extract constructor-level params
                    init_kwargs = {}
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

                    # Pass remaining kwargs to function, avoiding double-passing symbol

                    obj = cls(**init_kwargs)
                    func = getattr(obj, function_name)

                    # Filter clean_kwargs to only include parameters accepted by the function
                    import inspect

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

                    # Pass remaining kwargs to function, avoiding double-passing symbol
                    if symbol:
                        # Check if symbol was consumed by __init__
                        consumed_by_init = "symbol" in sig.parameters
                        # Check if symbol-like arg is in kwargs/args
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
                    # Filter UI internal parameters if they aren't part of the direct API function signature
                    import inspect

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
                    # Inspect constructor
                    import inspect

                    try:
                        sig = inspect.signature(cls.__init__)
                        init_kwargs = {}
                        for param in [
                            "symbol",
                            "symbol_id",
                            "random_agent",
                            "show_log",
                        ]:
                            if param in sig.parameters:
                                if param in ["symbol", "symbol_id"]:
                                    init_kwargs[param] = symbol
                                elif param in kwargs:
                                    init_kwargs[param] = kwargs.pop(param)
                        obj = cls(**init_kwargs)
                    except (ValueError, TypeError):
                        # Fallback for classes without __init__ or complex ones
                        obj = cls()
                    func = getattr(obj, function_name)
                else:
                    func = getattr(module, function_name)

                # Filter UI internal parameters and ensure only valid arguments are passed
                import inspect

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

            elif module_type == "connector":
                module = importlib.import_module(f"vnstock.connector.{sub_module}")
                cls = getattr(module, class_name)
                obj = cls()
                return getattr(obj, function_name)(*args, **kwargs)

        raise AttributeError(
            f"Method '{method_name}' not implemented for domain '{domain_name}'"
        )


class BaseDetailUI(BaseUI):
    """Base class for detail UI modules (e.g. Reference().company('VNM'))"""

    def __init__(self, symbol: str = None, **kwargs):
        self.symbol = symbol
        self.params = kwargs
