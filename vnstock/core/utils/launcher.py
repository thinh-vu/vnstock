import os
import platform
import subprocess
from typing import List, Optional

def change_dir(path: str) -> None:
    """
    Change the current working directory in the Python environment.

    Parameters:
        - path (str): Path to the new directory.
    
    Returns:
        - None
    """
    os.chdir(path)
    print(f'Changed directory to {path}')

def execute_command(command: Optional[List[str]] = None) -> None:
    """
    Execute a command on the system.

    Parameters:
        - command (Optional[List[str]]): List of command elements to execute.
          Default is None. Examples: ['ls', '-l'] or ['dir'] to list files
          in the current directory.
    """
    if command is None:
        command = ['echo', 'Hello, World!']
    
    # On Windows, prepend command with cmd.exe /c to handle internal
    # commands like dir
    if platform.system() == 'Windows':
        command = ['cmd.exe', '/c'] + command
    
    try:
        result = subprocess.run(
            command, check=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True
        )
        if result.stdout:
            print("Output:\n", result.stdout)
        if result.stderr:
            print("Error:\n", result.stderr)
    except subprocess.CalledProcessError as e:
        msg = f'Error executing command: {e}\nError Output:\n{e.stderr}'
        print(msg)
    except FileNotFoundError:
        print(f"Command not found: {' '.join(command)}")
