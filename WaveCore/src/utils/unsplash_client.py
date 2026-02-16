import requests
import os
from utils.constants import UNSPLASH_ACCESS_KEY

class UnsplashClient:
    BASE_URL = "https://api.unsplash.com/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}",
            "Accept-Version": "v1"
        })

    def search_photos(self, query, per_page=30, page=1):
        """
        Search for photos on Unsplash.
        """
        url = f"{self.BASE_URL}search/photos"
        params = {
            "query": query,
            "per_page": per_page,
            "page": page,
            "orientation": "landscape" # Best for our UI
        }
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            # Unsplash returns results in data['results']
            return data.get("results", [])
        except Exception as e:
            print(f"Unsplash Search Error: {e}")
            return []

    def download_file(self, url, target_path):
        """
        Download a file from Unsplash.
        Note: Unsplash requires triggering a download endpoint to satisfy their API guidelines,
        but for simple usage, downloading the image URL works.
        """
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"Unsplash Download Error: {e}")
            if os.path.exists(target_path):
                os.remove(target_path)
            return False
