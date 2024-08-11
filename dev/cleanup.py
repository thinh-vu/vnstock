import os
import shutil
import fnmatch

def delete_dirs(dirs):
    for dir in dirs:
        for root, dirnames, filenames in os.walk('.'):
            for dirname in fnmatch.filter(dirnames, dir):
                dir_path = os.path.join(root, dirname)
                try:
                    shutil.rmtree(dir_path)
                    print(f"Deleted directory: {dir_path}")
                except FileNotFoundError:
                    print(f"Directory not found: {dir_path}")
                except Exception as e:
                    print(f"Error while deleting directory: {dir_path}. Error: {str(e)}")

def delete_files(files):
    for file in files:
        for root, dirnames, filenames in os.walk('.'):
            for filename in fnmatch.filter(filenames, file):
                file_path = os.path.join(root, filename)
                try:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                except FileNotFoundError:
                    print(f"File not found: {file_path}")
                except Exception as e:
                    print(f"Error while deleting file: {file_path}. Error: {str(e)}")

# List of directories to delete
dirs_to_delete = ["__pycache__", "build", "*.egg-info", "dist"]

# List of files to delete
files_to_delete = ["*.tmp"]

# Delete directories
delete_dirs(dirs_to_delete)

# Delete files
delete_files(files_to_delete)