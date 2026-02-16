import requests
import os
import shutil

class PixabayClient:
    API_KEY = "49557127-3d1458eed8efc5713c99f8db0"
    BASE_URL = "https://pixabay.com/api/"
    VIDEO_URL = "https://pixabay.com/api/videos/"

    def __init__(self):
        self.session = requests.Session()

    def search_images(self, query, lang="es", per_page=200, page=1):
        """
        Search for images on Pixabay.
        """
        params = {
            "key": self.API_KEY,
            "q": query,
            "lang": lang,
            "image_type": "photo",
            "per_page": per_page,
            "page": page,
            "safesearch": "true"
        }
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("hits", [])
        except Exception as e:
            print(f"Pixabay Image Search Error: {e}")
            return []

    def search_videos(self, query, lang="es", per_page=200, page=1):
        """
        Search for videos on Pixabay.
        """
        params = {
            "key": self.API_KEY,
            "q": query,
            "lang": lang,
            "video_type": "all",
            "per_page": per_page,
            "page": page,
            "safesearch": "true"
        }
        try:
            response = self.session.get(self.VIDEO_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("hits", [])
        except Exception as e:
            print(f"Pixabay Video Search Error: {e}")
            return []

    def download_file(self, url, target_path):
        """
        Download a file from a URL to a local path.
        """
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"Download Error: {e}")
            if os.path.exists(target_path):
                os.remove(target_path)
            return False
