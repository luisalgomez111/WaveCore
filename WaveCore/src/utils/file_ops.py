import os
import shutil
# import send2trash # TODO: Add safely later
from PyQt6.QtWidgets import QMessageBox
from utils.constants import get_vault_path, get_audio_path, get_video_path, get_photo_path

def ensure_vault_exists():
    """Creates the Vault folder and subfolders if they doesn't exist. Returns the path."""
    vault_path = get_vault_path()
    paths = [vault_path, get_audio_path(), get_video_path(), get_photo_path()]
    
    for path in paths:
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as e:
                print(f"Error creating directory {path}: {e}")
                return None
    return vault_path


def create_new_folder(parent_path, name="New Folder"):
    """Creates a new folder. Returns info or raises error."""
    path = os.path.join(parent_path, name)
    counter = 1
    while os.path.exists(path):
        path = os.path.join(parent_path, f"{name} ({counter})")
        counter += 1
    
    os.makedirs(path)
    return path

def rename_item(old_path, new_name):
    """Renames a file or folder. Returns new path."""
    parent = os.path.dirname(old_path)
    new_path = os.path.join(parent, new_name)
    
    if os.path.exists(new_path):
        raise FileExistsError(f"'{new_name}' already exists.")
    
    os.rename(old_path, new_path)
    return new_path

def delete_item(path):
    """Deletes a file or folder permanently (or sends to trash if possible)."""
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

def move_file(source_path, target_folder):
    """Moves a file to a target folder."""
    filename = os.path.basename(source_path)
    target_path = os.path.join(target_folder, filename)
    
    if os.path.exists(target_path):
        raise FileExistsError(f"'{filename}' already exists in destination.")
        
    shutil.move(source_path, target_path)
    return target_path
