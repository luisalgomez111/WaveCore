import json
import os

class FavoritesManager:
    def __init__(self, config_dir=None):
        if config_dir is None:
            # Default to user app data or local .gemini/settings
            config_dir = os.path.join(os.path.expanduser("~"), ".dr_audio")
        
        self.config_path = os.path.join(config_dir, "favorites.json")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        self.favorites = self._load()

    def _load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()

    def _save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(list(self.favorites), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving favorites: {e}")

    def add(self, path):
        if path:
            self.favorites.add(path)
            self._save()

    def remove(self, path):
        if path in self.favorites:
            self.favorites.remove(path)
            self._save()

    def is_favorite(self, path):
        return path in self.favorites

    def toggle(self, path):
        if self.is_favorite(path):
            self.remove(path)
            return False
        else:
            self.add(path)
            return True

    def get_all(self):
        return list(self.favorites)
