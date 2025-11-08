def help(obj, method_path):
    """
    Display detailed information about a method in the specified object
    based on its name.

    Parameters:
    - obj: Object containing the method to retrieve information about.
    - method_path: Path to the method as a dot-separated string,
                   e.g., 'module.class.method'.
    """
    parts = method_path.split('.')
    current_obj = obj
    for part in parts[:-1]:
        try:
            current_obj = getattr(current_obj, part)
        except AttributeError:
            msg = f"Attribute '{part}' not found in "
            msg += f"'{current_obj.__class__.__name__}'."
            print(msg)
            return
    
    method_name = parts[-1]
    try:
        method = getattr(current_obj, method_name)
        import inspect
        print(inspect.getdoc(method))
    except AttributeError:
        msg = f"Method or attribute '{method_name}' not found in "
        msg += f"'{current_obj.__class__.__name__}'."
        print(msg)
