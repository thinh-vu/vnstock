import importlib
from types import MethodType

def load_extensions(target_instance, module_name, function_names):
    """
    Dynamically import functions from a specified module and bind them to the target instance.

    Parameters:
        - target_instance: The instance of the class to bind these functions to.
        - module_name: The name of the module to import, relative to the package.
        - function_names: A list of function names as strings that should be imported and bound.
    Usage:
    ```
    from vnstock.core.utils.ext import load_extensions

    class Trading:
        def __init__(self, symbol):
            self.symbol = symbol
            load_extensions(self, '.core.utils', ['calculate_average_price'])
    ```
    """
    module = importlib.import_module(module_name, __package__)
    for func_name in function_names:
        if hasattr(module, func_name):
            func = getattr(module, func_name)
            setattr(target_instance, func_name, MethodType(func, target_instance))

def check_plugins_installed(plugins):
    """
    Check whether a list of vnstock plugins package are installed, return installed package names as a list.

    Parameters:
        - plugins: A list of package names to check for installation.
    """
    installed_plugins = []
    for plugin in plugins:
        try:
            importlib.import_module(plugin)
            installed_plugins.append(plugin)
        except ImportError:
            pass
    # if installed_plugins is empty, print a message to the user
    if not installed_plugins:
        print("No plugins in the list are installed.")
    return installed_plugins