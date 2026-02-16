import os

APP_NAME = "WaveCore"
VERSION = "2.0.0"
VAULT_FOLDER_NAME = "WaveCore Vault"

def get_vault_path():
    """Returns the absolute path to the user's Documents/WaveCore folder."""
    docs_dir = os.path.expanduser("~/Documents")
    return os.path.join(docs_dir, APP_NAME)

def get_audio_path():
    return os.path.join(get_vault_path(), "Audio")

def get_video_path():
    return os.path.join(get_vault_path(), "Videos")

def get_photo_path():
    return os.path.join(get_vault_path(), "Photos")

FREESOUND_API_KEY = "xDufLi4YCGmcKas3q61Jo7Vx3JUyvwLWiUDzm941"
PEXELS_API_KEY = "F3zbp8xBr2RwnF6EE5F9UAWt5l7KtqLjhJ6an8R7aDSnsWDfe8T9DH0n"
UNSPLASH_ACCESS_KEY = "z6pjOgkYZ2SJ8qlFZqH4xEPszhad1xIfRwzrKML1RZA"
FREEPIK_API_KEY = "" # DELETED

# Support & Donations
PAYPAL_URL = "https://www.paypal.me/LGomez1991"
BINANCE_ADR = "luisalbertogomez111@gmail.com"

