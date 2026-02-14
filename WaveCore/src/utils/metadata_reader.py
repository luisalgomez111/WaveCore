import os
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE

def get_track_metadata(file_path):
    """
    Reads metadata from an audio file.
    Returns a dict with keys: 
    title, artist, album, genre, duration, bitrate, sample_rate, channels.
    """
    meta = {
        "title": os.path.basename(file_path), # Default to filename
        "artist": "",
        "album": "",
        "genre": "",
        "duration": 0,
        "bitrate": 0,
        "sample_rate": 0,
        "channels": 0
    }
    
    if not os.path.exists(file_path):
        return meta
        
    try:
        # Generic Mutagen Load
        f = mutagen.File(file_path)
        if not f:
            return meta
            
        # Duration/Technical
        if f.info:
            meta["duration"] = getattr(f.info, "length", 0)
            meta["bitrate"] = getattr(f.info, "bitrate", 0) / 1000.0 # kbps
            meta["sample_rate"] = getattr(f.info, "sample_rate", 0)
            meta["channels"] = getattr(f.info, "channels", 0)
            
        # Tags
        # Mutagen handles different formats differently.
        # EasyID3 is good for MP3 standard tags.
        tags = f.tags or {}
        
        # Helper to extract first item of list or string
        def get_tag(keys):
            for key in keys:
                if key in tags:
                    val = tags[key]
                    if isinstance(val, list):
                        return str(val[0])
                    return str(val)
            return ""
            
        # Common keys across formats (ID3 vs Vorbis vs etc)
        # ID3: TIT2, TPE1, TALB, TCON
        # Vorbis: TITLE, ARTIST, ALBUM, GENRE
        
        # Title
        t = get_tag(["TIT2", "title", "TITLE"])
        if t: meta["title"] = t
        
        # Artist
        a = get_tag(["TPE1", "artist", "ARTIST"])
        if a: meta["artist"] = a
        
        # Album
        al = get_tag(["TALB", "album", "ALBUM"])
        if al: meta["album"] = al
        
        # Genre
        g = get_tag(["TCON", "genre", "GENRE"])
        if g: meta["genre"] = g
        
    except Exception as e:
        print(f"Metadata error {file_path}: {e}")
        
    return meta
