
from PyQt6.QtCore import QThread, pyqtSignal
import os
import time
from core.asset_models import AudioAsset, VideoAsset, ImageAsset

class ScannerThread(QThread):
    # Signals
    batch_found = pyqtSignal(list) 
    finished_scan = pyqtSignal(int)

    def __init__(self, folder_path=None, file_paths=None):
        super().__init__()
        self.folder_path = folder_path
        self.file_paths = file_paths
        self._is_running = True
        
        self.audio_ext = ('.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aiff')
        self.video_ext = ('.mp4', '.mov', '.avi', '.mkv', '.webm')
        self.image_ext = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')

    def run(self):
        batch_size = 20
        current_batch = []
        total_count = 0
        
        try:
            if self.folder_path:
                with os.scandir(self.folder_path) as it:
                    for entry in it:
                        if not self._is_running: break
                        if entry.is_file():
                            ext = os.path.splitext(entry.name)[1].lower()
                            if ext in self.audio_ext or ext in self.video_ext or ext in self.image_ext:
                                self._process_file(entry.path, entry.name, ext, current_batch)
                                total_count += 1
                                if len(current_batch) >= batch_size:
                                    self.batch_found.emit(current_batch)
                                    current_batch = []
                                    time.sleep(0.001)
            elif self.file_paths:
                for path in self.file_paths:
                    if not self._is_running: break
                    if os.path.exists(path):
                        ext = os.path.splitext(path)[1].lower()
                        if ext in self.audio_ext or ext in self.video_ext or ext in self.image_ext:
                            self._process_file(path, os.path.basename(path), ext, current_batch)
                            total_count += 1
                            if len(current_batch) >= batch_size:
                                self.batch_found.emit(current_batch)
                                current_batch = []

            if current_batch:
                self.batch_found.emit(current_batch)
                
        except Exception as e:
            print(f"Scanner Error: {e}")
            import traceback
            traceback.print_exc()
            
        self.finished_scan.emit(total_count)

    def _process_file(self, path, name, ext, batch):
        try:
            asset = None
            
            if ext in self.audio_ext:
                from utils.audio_loader import load_waveform_data
                from utils.metadata_reader import get_track_metadata
                
                # Load Audio Data
                try:
                    data, duration, chans = load_waveform_data(path, points=400)
                except:
                    data, duration, chans = None, 0, 0
                
                meta = get_track_metadata(path)
                final_duration = meta.get("duration", 0)
                if final_duration == 0: final_duration = duration
                
                asset = AudioAsset(path, duration=final_duration)
                asset.waveform = data
                asset.channels = "Stereo" if chans > 1 else "Mono"
                asset.title = meta.get("title", name) # Override title if metadata exists
                
            elif ext in self.video_ext:
                from utils.video_utils import VideoMetadataExtractor
                
                # Extract Metadata & Thumbnail
                extractor = VideoMetadataExtractor()
                meta = extractor.get_metadata(path)
                
                asset = VideoAsset(path)
                asset.duration = meta.get("duration", 0)
                asset.width = meta.get("width", 0)
                asset.height = meta.get("height", 0)
                asset.fps = meta.get("fps", 0)
                asset.thumbnail_path = meta.get("thumbnail_path", "")
                
                # Title from filename if not in metadata (OpenCV doesn't give title usually)
                asset.title = name
                
            elif ext in self.image_ext:
                # Placeholder for Image Extraction
                asset = ImageAsset(path)
            
            if asset:
                # COMPATIBILITY LAYER:
                # Convert the object to a dict structure that LibraryModel expects
                # LibraryModel expects: path, title, duration, format, channels, waveform, is_favorite
                
                track_data = asset.to_dict()
                
                # Add extra fields expected by current UI if missing
                if "artist" not in track_data: track_data["artist"] = ""
                if "album" not in track_data: track_data["album"] = ""
                if "channels" not in track_data: track_data["channels"] = ""
                
                batch.append(track_data)
                
        except Exception as e:
            print(f"Error processing {name}: {e}")

    def stop(self):
        self._is_running = False
        self.wait()
