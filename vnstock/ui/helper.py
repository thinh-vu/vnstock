"""
Helper utilities for vnstock Unified UI.
"""

import importlib.util
from typing import Optional, Any, Type

def is_sponsor_installed() -> bool:
    """Check if vnstock_data (sponsor package) is installed."""
    return importlib.util.find_spec('vnstock_data') is not None



def get_sponsor_ui_class(module_name: str, class_name: str) -> Optional[Type]:
    """
    Attempt to get the equivalent UI class from vnstock_data.
    
    Args:
        module_name: The submodule name (e.g., 'reference', 'market')
        class_name: The class name (e.g., 'Reference', 'Market')
        
    Returns:
        The class from vnstock_data.ui if available, else None.
    """
    if not is_sponsor_installed():
        return None
        
    try:
        # Construct the import path for vnstock_data.ui
        sponsor_import_path = f"vnstock_data.ui.{module_name}"
        module = importlib.import_module(sponsor_import_path)
        return getattr(module, class_name, None)
    except BaseException:
        # Catch all including SystemExit to avoid crashing free package if sponsor is broken
        return None

def redirect_if_sponsor(module_name: str, class_name: str):
    """
    Decorator for UI class __new__ to redirect to vnstock_data if available.
    """
    def wrapper(cls, *args, **kwargs):
        sponsor_cls = get_sponsor_ui_class(module_name, class_name)
        if sponsor_cls:
            return sponsor_cls(*args, **kwargs)
        # Fallback to current class
        return super(cls, cls).__new__(cls)
    return wrapper

def show_doc(obj: Any) -> None:
    """
    Displays the documentation for a function, method, or class.
    """
    import inspect
    
    # Resolve string to class if needed
    if isinstance(obj, str):
        from vnstock import ui
        try:
            parts = obj.split('.')
            curr = ui
            for p in parts:
                curr = getattr(curr, p)
            obj = curr
        except (AttributeError, ImportError):
            print(f"Could not resolve: {obj}")
            return

    try:
        sig = inspect.signature(obj)
        print(f"Signature: \033[92m{obj.__name__}{sig}\033[0m\n")
    except (ValueError, TypeError, AttributeError):
        pass
    
    doc = inspect.getdoc(obj)
    if doc:
        print(doc)
    else:
        print("No documentation available.")

def show_api(node: Any = None, level: int = 0) -> None:
    """
    Display the API structure tree for vnstock.
    Matches the presentation style of vnstock_data.
    """
    from vnstock.ui._registry import MAP
    from vnstock.ui.helper import get_sponsor_ui_class, check_sponsor_package
    import inspect
    
    if node is None:
        import vnstock.ui as ui
        print("\nAPI STRUCTURE TREE - VNSTOCK (Unified UI)")
        print("vnstock")
        for attr in ["Reference", "Market", "Fundamental", "Retail", "Broker"]:
            try:
                cls_obj = getattr(ui, attr)()
                # Colorize top level domains (Bold Cyan)
                print(f"├── \033[1;36m{attr}\033[0m")
                show_api(cls_obj, level + 1)
            except:
                print(f"├── {attr}")
        return

    # Recursive display for sub-nodes
    indent = "│   " * level
    
    # Identify domain from class name
    cls_name = type(node).__name__
    domain_map = {
        "Reference": "Reference",
        "CompanyReference": "company",
        "EquityReference": "equity", 
        "IndexReference": "index",
        "ETFReference": "etf", 
        "WarrantReference": "warrant",
        "FuturesReference": "futures", 
        "BondReference": "bond",
        "FundReference": "fund", 
        "IndustryReference": "industry",
        "MarketReference": "market", 
        "SearchReference": "search",
        "EventReference": "events",
        "ForexReference": "forex",
        
        "Market": "Market",
        "EquityMarket": "equity", 
        "IndexMarket": "index",
        "ETFMarket": "etf",
        "FuturesMarket": "futures", 
        "WarrantMarket": "warrant",
        "FundMarket": "fund", 
        "CryptoMarket": "crypto",
        "CommodityMarket": "commodity",
        "ForexMarket": "forex",
        
        "Fundamental": "Fundamental", 
        "EquityFundamental": "equity",
        "Retail": "Retail", 
        "Broker": "Broker", 
        "DNSE": "dnse", 
        "DNSEBroker": "dnse"
    }
    
    # Parent domain detection
    parent_domain = getattr(node, '_parent_domain', None)
    if not parent_domain:
        if "Reference" in cls_name and cls_name != "Reference":
            parent_domain = "Reference"
        elif "Market" in cls_name and cls_name != "Market":
            parent_domain = "Market"
        elif "Fundamental" in cls_name and cls_name != "Fundamental":
            parent_domain = "Fundamental"
        elif "Broker" in cls_name and cls_name != "Broker":
            parent_domain = "Broker"

    domain = domain_map.get(cls_name)
    
    # Identify sub-domains vs methods
    all_members_raw = [n for n in dir(node) if not n.startswith('_')]
    
    # Pre-classify to know what is what
    member_types = {}
    instrument_names = [
        'company', 'index', 'forex', 'equity', 'etf', 'futures', 
        'warrant', 'bond', 'fund', 'industry', 'market', 'search', 
        'dnse', 'crypto', 'commodity'
    ]
    for n in all_members_raw:
        member = getattr(node, n)
        if inspect.ismethod(member):
            sig = inspect.signature(member)
            is_sub = any(x in str(sig.return_annotation) for x in ['Market', 'Reference', 'Status', 'Engine'])
            # Automatic sub-domain detection: if it returns something in our domain_map or is a known instrument
            if is_sub or n in instrument_names:
                member_types[n] = 'sub'
            else:
                member_types[n] = 'method'
        elif isinstance(getattr(type(node), n, None), property):
            member_types[n] = 'sub'
        else:
            member_types[n] = 'other'

    # Order by Registry
    registry_keys = []
    if parent_domain in MAP and domain in MAP[parent_domain]:
        registry_keys = list(MAP[parent_domain][domain].keys())
    elif domain in MAP:
        registry_keys = list(MAP[domain].keys())

    # Final ordered list of members to display
    def get_order_key(name):
        try:
            return registry_keys.index(name)
        except ValueError:
            return 999 

    members_to_show = [m for m in all_members_raw if m in member_types and member_types[m] != 'other']
    members_to_show.sort(key=lambda x: (get_order_key(x), x))

    # Single loop for discovery
    for i, m_name in enumerate(members_to_show):
        is_last = (i == len(members_to_show) - 1)
        prefix = "└── " if is_last else "├── "
        m_type = member_types[m_name]

        # RECURSION LOGIC (Nodes)
        if m_type == 'sub' or m_name in instrument_names:
            try:
                member_attr = getattr(node, m_name)
                sub_obj = None
                
                # Get description from docstring
                doc = inspect.getdoc(member_attr)
                if not doc and hasattr(member_attr, '__doc__'):
                    doc = member_attr.__doc__
                desc = f" # {doc.split('.')[0]}." if doc else ""

                if inspect.ismethod(member_attr):
                    sig = inspect.signature(member_attr)
                    # Try to call it to see if it returns a domain object
                    if 'symbol' in sig.parameters:
                        sym = getattr(node, 'symbol', 'VNM')
                        sub_obj = member_attr(symbol=sym)
                    else:
                        sub_obj = member_attr()
                else:
                    sub_obj = member_attr
                
                # Verify if it's a domain object we should recurse into
                sub_cls_name = type(sub_obj).__name__
                if sub_obj and sub_cls_name in domain_map and sub_cls_name not in ['DataFrame', 'Series', 'type']:
                    # Special Case: Prevent duplicate/infinite recursion (e.g. Reference under Reference)
                    if sub_cls_name == cls_name:
                        continue
                    if level == 0 and sub_cls_name in ["Reference", "Market", "Fundamental", "Retail", "Broker"]:
                        show_api(sub_obj, level + 1)
                        continue

                    # Success: Print node name (with docstring) and recurse
                    # Colorize sub-domains (Bold Yellow)
                    print(f"{indent}{prefix}\033[1;33m{m_name}\033[0m{desc}")
                    # Capture real parent domain
                    new_parent_domain = parent_domain if parent_domain else domain
                    sub_obj._parent_domain = new_parent_domain
                    show_api(sub_obj, level + 1)
                    continue
            except:
                pass

        # LEAF METHOD DISPLAY
        meta = None
        registry_domain = domain
        # Precise matching for multi-layer domains
        if parent_domain in MAP:
            if domain in MAP[parent_domain] and m_name in MAP[parent_domain][domain]:
                meta = MAP[parent_domain][domain][m_name]
                registry_domain = domain
        elif domain in MAP and m_name in MAP[domain]:
            meta = MAP[domain][m_name]
            registry_domain = domain
        
        if meta and len(meta) >= 7:
            layer, sub_mod, cls, func, source, r_type, summary = meta
            print(f"{indent}{prefix}{m_name}() [{source}] -> {r_type} # {summary}")
        elif m_type != 'sub' and m_name not in instrument_names:
            # Get description from docstring fallback
            member_attr = getattr(node, m_name, None)
            doc = inspect.getdoc(member_attr) if member_attr else None
            # Fix: don't split if None
            clean_doc = doc.split('.')[0] if doc else ""
            desc = f" # {clean_doc}." if clean_doc else ""
            print(f"{indent}{prefix}{m_name}(){desc}")

def check_sponsor_package() -> bool:
    """Helper to check if sponsor package is available."""
    import importlib.util
    return importlib.util.find_spec('vnstock_data') is not None
