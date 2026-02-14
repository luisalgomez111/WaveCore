import os

APP_NAME = "WaveCore"
VERSION = "1.0.1"
VAULT_FOLDER_NAME = "WaveCore Vault"

def get_vault_path():
    """Returns the absolute path to the user's Music/WaveCore Vault folder."""
    music_dir = os.path.expanduser("~/Music")
    return os.path.join(music_dir, VAULT_FOLDER_NAME)

FREESOUND_API_KEY = "xDufLi4YCGmcKas3q61Jo7Vx3JUyvwLWiUDzm941"

