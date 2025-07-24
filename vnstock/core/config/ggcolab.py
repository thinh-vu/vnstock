import os
import shutil
from pathlib import Path
from .utils.env import get_hosting_service


def get_vnstock_data_dir():
    """
    Trả về thư mục lưu trữ dữ liệu vnstock, ưu tiên lấy từ biến môi trường VNSTOCK_DATA_DIR.
    Nếu không có thì mặc định là ~/.vnstock
    """
    data_dir = os.environ.get("VNSTOCK_DATA_DIR")
    if data_dir:
        return Path(data_dir).expanduser().resolve()
    return Path.home() / ".vnstock"


def migrate_vnstock_data_colab(new_dir=None):
    """
    Di chuyển dữ liệu ~/.vnstock sang thư mục mới trong Google Drive (chỉ dùng cho Google Colab).
    new_dir: Đường dẫn tuyệt đối tới thư mục mới (mặc định: /content/drive/MyDrive/.vnstock)
    
    Raises:
        RuntimeError: Nếu không chạy trong môi trường Google Colab
    """
    # Kiểm tra môi trường chạy
    if get_hosting_service() != "Google Colab":
        raise RuntimeError("Hàm này chỉ có thể chạy trong môi trường Google Colab")

    # Mount Google Drive nếu chưa được mount
    from google.colab import drive
    drive.mount('/content/drive')

    # Sử dụng thư mục mặc định trong Google Drive nếu không chỉ định new_dir
    if new_dir is None:
        new_dir = "/content/drive/MyDrive/.vnstock"
    
    if not isinstance(new_dir, (str, Path)):
        raise TypeError("new_dir phải là chuỗi hoặc đối tượng Path")

    old_dir = Path.home() / ".vnstock"
    new_dir = Path(new_dir).expanduser().resolve()
    if not old_dir.exists():
        print(f"Không tìm thấy thư mục dữ liệu cũ: {old_dir}")
        return
    os.makedirs(new_dir, exist_ok=True)

    if not new_dir.parent.exists():
        raise FileNotFoundError(f"Thư mục cha của {new_dir} không tồn tại")

    # Copy toàn bộ dữ liệu
    try:
        for item in old_dir.iterdir():
            dest = new_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
    except (shutil.Error, OSError) as e:
        raise RuntimeError(f"Lỗi khi sao chép dữ liệu: {str(e)}")

    # Tự động set biến môi trường
    os.environ['VNSTOCK_DATA_DIR'] = str(new_dir)
    print(f"Đã set VNSTOCK_DATA_DIR={str(new_dir)}")
