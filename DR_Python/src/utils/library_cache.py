import os
import json
import hashlib

CACHE_FILE = os.path.join(os.path.expanduser("~"), ".wavecore_cache.json")

def _get_folder_hash(folder_path):
    # Simply use the absolute path as key for now
    # A better approach would be hashing path + mtime of the folder
    return hashlib.md5(folder_path.encode()).hexdigest()

def get_cached_folder_data(folder_path):
    folder_path = os.path.normpath(folder_path)
    if not os.path.exists(CACHE_FILE):
        return None
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            full_cache = json.load(f)
            return full_cache.get(folder_path)
    except:
        return None

def save_folder_to_cache(folder_path, tracks):
    folder_path = os.path.normpath(folder_path)
    try:
        full_cache = {}
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                full_cache = json.load(f)
        
        # We store only essential data. 
        # Waveforms are already small arrays (400 floats)
        # We convert numpy arrays to lists for JSON
        serializable_tracks = []
        for t in tracks:
            t_copy = t.copy()
            if hasattr(t["waveform"], "tolist"):
                t_copy["waveform"] = t["waveform"].tolist()
            # Remove any non-serializable objects like QPainterPath cache
            if "_wave_path_cache" in t_copy:
                del t_copy["_wave_path_cache"]
            serializable_tracks.append(t_copy)
            
        full_cache[folder_path] = serializable_tracks
        
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(full_cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Cache Save Error: {e}")

def invalidate_cache(folder_path):
    folder_path = os.path.normpath(folder_path)
    try:
        if not os.path.exists(CACHE_FILE):
            return
            
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            full_cache = json.load(f)
            
        if folder_path in full_cache:
            del full_cache[folder_path]
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(full_cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Cache Invalidation Error: {e}")
