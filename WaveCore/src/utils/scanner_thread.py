
from PyQt6.QtCore import QThread, pyqtSignal
import os
import time

class ScannerThread(QThread):
    # Signals
    batch_found = pyqtSignal(list) 
    finished_scan = pyqtSignal(int)

    def __init__(self, folder_path=None, file_paths=None):
        super().__init__()
        self.folder_path = folder_path
        self.file_paths = file_paths
        self._is_running = True

    def run(self):
        from utils.metadata_reader import get_track_metadata
        from utils.audio_loader import load_waveform_data

        supported_ext = ('.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aiff')
        batch_size = 20
        current_batch = []
        total_count = 0
        
        try:
            if self.folder_path:
                with os.scandir(self.folder_path) as it:
                    for entry in it:
                        if not self._is_running: break
                        if entry.is_file() and entry.name.lower().endswith(supported_ext):
                            self._process_file(entry.path, entry.name, current_batch)
                            total_count += 1
                            if len(current_batch) >= batch_size:
                                self.batch_found.emit(current_batch)
                                current_batch = []
                                time.sleep(0.001)
            elif self.file_paths:
                for path in self.file_paths:
                    if not self._is_running: break
                    if os.path.exists(path):
                        self._process_file(path, os.path.basename(path), current_batch)
                        total_count += 1
                        if len(current_batch) >= batch_size:
                            self.batch_found.emit(current_batch)
                            current_batch = []

            if current_batch:
                self.batch_found.emit(current_batch)
                
        except Exception as e:
            print(f"Scanner Error: {e}")
            
        self.finished_scan.emit(total_count)

    def _process_file(self, path, name, batch):
        from utils.metadata_reader import get_track_metadata
        from utils.audio_loader import load_waveform_data

        meta = get_track_metadata(path)
        try:
            data, duration, chans = load_waveform_data(path, points=400)
        except:
            data, duration, chans = None, 0, 0
        
        if meta.get("duration", 0) == 0:
            meta["duration"] = duration

        track_data = {
            "path": path,
            "title": meta.get("title", name),
            "artist": meta.get("artist", ""),
            "album": meta.get("album", ""),
            "duration": meta.get("duration", 0),
            "format": os.path.splitext(name)[1].upper().replace(".", ""),
            "channels": "Stereo" if chans > 1 else "Mono" if chans == 1 else "Unknown",
            "waveform": data
        }
        batch.append(track_data)

    def stop(self):
        self._is_running = False
        self.wait()
