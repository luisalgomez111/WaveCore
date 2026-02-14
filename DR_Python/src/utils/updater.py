import requests
from utils.constants import VERSION

GITHUB_REPO = "luisalgomez111/WaveCore"

def check_for_updates():
    """
    Checks GitHub Releases for a newer version.
    Returns: (bool: update_available, str: latest_version, str: download_url)
    """
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get("tag_name", "0.0.0").replace("v", "")
            
            # Simple version comparison (e.g., "1.0.1" > "1.0.0")
            if latest_version > VERSION:
                # Find the .exe or installer in assets
                download_url = None
                for asset in data.get("assets", []):
                    if asset["name"].endswith(".exe"):
                        download_url = asset["browser_download_url"]
                        break
                
                return True, latest_version, download_url
    except Exception as e:
        print(f"Update check failed: {e}")
    
    return False, VERSION, None
