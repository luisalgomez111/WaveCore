import requests
from utils.constants import PEXELS_API_KEY

class PexelsClient:
    BASE_URL = "https://api.pexels.com/v1/"
    VIDEO_URL = "https://api.pexels.com/videos/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Authorization": PEXELS_API_KEY})

    def search_videos(self, query, per_page=80, page=1):
        url = f"{self.VIDEO_URL}search"
        params = {
            "query": query,
            "per_page": per_page,
            "page": page,
            "orientation": "landscape" # Prefer landscape for videos
        }
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("videos", [])
        except Exception as e:
            print(f"Pexels Video Search Error: {e}")
            return []

    def search_photos(self, query, per_page=80, page=1):
        url = f"{self.BASE_URL}search"
        params = {
            "query": query,
            "per_page": per_page,
            "page": page
        }
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("photos", [])
        except Exception as e:
            print(f"Pexels Photo Search Error: {e}")
            return []

    def download_file(self, url, target_path):
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"Download Error: {e}")
            return False
