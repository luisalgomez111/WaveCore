import requests
import os
from utils.constants import FREESOUND_API_KEY

class FreesoundClient:
    BASE_URL = "https://freesound.org/apiv2"

    def __init__(self):
        self.api_key = FREESOUND_API_KEY
    
    def search_sounds(self, query, page=1, page_size=150):
        """
        Search for sounds in Freesound.
        Returns a list of dicts with basic info and preview URLs.
        """
        url = f"{self.BASE_URL}/search/text/"
        params = {
            "query": query,
            "token": self.api_key,
            "page": page,
            "page_size": page_size,
            "fields": "id,name,previews,duration,username,type,images" 
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            print(f"Freesound Search Error: {e}")
            return []

    def download_preview(self, url, target_path):
        """
        Downloads a preview file (MP3) to the target path.
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"Download Error: {e}")
            return False
