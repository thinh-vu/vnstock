import os
import platform
import subprocess
from typing import List, Optional

def change_dir(path: str) -> None:
    """
    Thay đổi thư mục làm việc hiện tại trong môi trường Python.

    Tham số:
        - path (str): Đường dẫn tới thư mục mới.
    
    Trả về:
        - None
    """
    os.chdir(path)
    print(f'Changed directory to {path}')

def execute_command(command: Optional[List[str]] = None) -> None:
    """
    Thực thi một lệnh trên hệ thống.

    Tham số:
        - command (Optional[List[str]]): Danh sách các phần tử của lệnh cần thực thi. Mặc định là None. Ví dụ: ['ls', 'l'] hoặc ['dir'] để hiển thị danh sách tệp tin trong thư mục hiện tại.
    """
    if command is None:
        command = ['echo', 'Hello, World!']
    
    # On Windows, prepend command with cmd.exe /c to handle internal commands like dir
    if platform.system() == 'Windows':
        command = ['cmd.exe', '/c'] + command
    
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.stdout:
            print("Output:\n", result.stdout)
        if result.stderr:
            print("Error:\n", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f'Error executing command: {e}\nError Output:\n{e.stderr}')
    except FileNotFoundError:
        print(f"Command not found: {' '.join(command)}")