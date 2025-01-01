def help(obj, method_path):
    """
    Hiển thị thông tin chi tiết về một phương thức trong đối tượng được chỉ định dựa trên tên của nó.

    Tham số:
    - obj: Đối tượng chứa phương thức cần tìm thông tin.
    - method_path: Đường dẫn đến phương thức dưới dạng chuỗi phân tách bằng dấu chấm, ví dụ: 'module.class.method'.
    """
    parts = method_path.split('.')
    current_obj = obj
    for part in parts[:-1]:
        try:
            current_obj = getattr(current_obj, part)
        except AttributeError:
            print(f"Thuộc tính '{part}' không được tìm thấy trong '{current_obj.__class__.__name__}'.")
            return
    
    method_name = parts[-1]
    try:
        method = getattr(current_obj, method_name)
        import inspect
        print(inspect.getdoc(method))
    except AttributeError:
        print(f"Phương thức hoặc thuộc tính '{method_name}' không được tìm thấy trong '{current_obj.__class__.__name__}'.")