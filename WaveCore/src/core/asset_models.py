import os
import json
import time

class Asset:
    """Base class for all media assets."""
    def __init__(self, path):
        self.path = os.path.normpath(path)
        self.filename = os.path.basename(path)
        self.title = os.path.splitext(self.filename)[0]
        self.file_size = os.path.getsize(path) if os.path.exists(path) else 0
        self.mtime = os.path.getmtime(path) if os.path.exists(path) else 0
        self.tags = []
        self.is_favorite = False
        self.type = "generic"

    def to_dict(self):
        """Serialize explicitly for JSON cache."""
        return {
            "type": self.type,
            "path": self.path,
            "filename": self.filename,
            "title": self.title,
            "file_size": self.file_size,
            "mtime": self.mtime,
            "tags": self.tags,
            "is_favorite": self.is_favorite
        }
    
    @classmethod
    def from_dict(cls, data):
        """Factory method to recreate asset from dict."""
        # This should be implemented by subclasses or a factory
        pass

class AudioAsset(Asset):
    def __init__(self, path, duration=0, channels=1, sample_rate=44100, waveform=None):
        super().__init__(path)
        self.type = "audio"
        self.duration = duration
        self.channels = channels
        self.sample_rate = sample_rate
        self.waveform = waveform # Expects list or numpy array
        self.format = os.path.splitext(path)[1].lower().replace(".", "")

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "duration": self.duration,
            "channels": self.channels,
            "sample_rate": self.sample_rate,
            "waveform": self.waveform, # Ensure this is a list before saving
            "format": self.format
        })
        return data

class VideoAsset(Asset):
    def __init__(self, path, duration=0, width=0, height=0, fps=0.0, thumbnail_path=""):
        super().__init__(path)
        self.type = "video"
        self.duration = duration
        self.width = width
        self.height = height
        self.fps = fps
        self.thumbnail_path = thumbnail_path
        self.format = os.path.splitext(path)[1].lower().replace(".", "")

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "thumbnail_path": self.thumbnail_path,
            "format": self.format
        })
        return data

class ImageAsset(Asset):
    def __init__(self, path, width=0, height=0, format=""):
        super().__init__(path)
        self.type = "image"
        self.width = width
        self.height = height
        self.format = format or os.path.splitext(path)[1].lower().replace(".", "")

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "width": self.width,
            "height": self.height,
            "format": self.format
        })
        return data
