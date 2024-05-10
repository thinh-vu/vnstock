# Perform cleanup of the package directory prior to committing to GitHub
# Run from Github Codespace: python3 /workspaces/vnstock/dev/cleanup.py

import os
import shutil

def delete_dirs(dirs):
    for dir in dirs:
        try:
            shutil.rmtree(dir)
            print(f"Deleted directory: {dir}")
        except FileNotFoundError:
            print(f"Directory not found: {dir}")
        except Exception as e:
            print(f"Error while deleting directory: {dir}. Error: {str(e)}")

def delete_files(files):
    for file in files:
        try:
            os.remove(file)
            print(f"Deleted file: {file}")
        except FileNotFoundError:
            print(f"File not found: {file}")
        except Exception as e:
            print(f"Error while deleting file: {file}. Error: {str(e)}")

# List of directories to delete
dirs_to_delete = ["__pycache__", "build", "dist", "*.egg-info"]

# List of files to delete
files_to_delete = []

# Delete directories
delete_dirs(dirs_to_delete)

# Delete files
delete_files(files_to_delete)
