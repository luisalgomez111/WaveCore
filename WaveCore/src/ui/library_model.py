from PyQt6.QtCore import QAbstractTableModel, Qt, pyqtSignal, QModelIndex, QMimeData, QUrl
import os
from constants import LibraryColumns

class LibraryModel(QAbstractTableModel):
    # Use Constants for architectural stability
    COL_INDEX = LibraryColumns.INDEX
    COL_FAV = LibraryColumns.FAV
    COL_PLAY = LibraryColumns.PLAY
    COL_TITLE = LibraryColumns.TITLE
    COL_CHANNELS = LibraryColumns.CHANNELS
    COL_FORMAT = LibraryColumns.FORMAT
    COL_DURATION = LibraryColumns.DURATION
    COL_WAVEFORM = LibraryColumns.WAVEFORM
    
    COL_COUNT = LibraryColumns.COUNT
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tracks = [] # List of dicts
        self._playing_index = -1
        
    def add_tracks(self, tracks):
        if not tracks: return
        start = len(self._tracks)
        end = start + len(tracks) - 1
        
        self.beginInsertRows(QModelIndex(), start, end)
        self._tracks.extend(tracks)
        self.endInsertRows()
        
    def rowCount(self, parent=QModelIndex()):
        if parent.isValid(): return 0
        return len(self._tracks)
        
    def columnCount(self, parent=QModelIndex()):
        return self.COL_COUNT
        
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._tracks)):
            return None
            
        track = self._tracks[index.row()]
        col = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            if col == self.COL_INDEX:
                return str(index.row() + 1)
            elif col == self.COL_TITLE:
                return track.get("title", "")
            elif col == self.COL_CHANNELS:
                return track.get("channels", "")
            elif col == self.COL_FORMAT:
                return track.get("format", "")
            elif col == self.COL_DURATION:
                d = track.get("duration", 0)
                m = int(d // 60)
                s = int(d % 60)
                return f"{m:02d}:{s:02d}"
            # Play and Waveform are custom painted, no text needed
            return ""
            
        # Custom roles for Delegate
        elif role == Qt.ItemDataRole.UserRole:
            # Return full track data for logic
            return track
            
        elif role == Qt.ItemDataRole.UserRole + 2:
            # Is Favorite?
            return track.get("is_favorite", False)
            
        return None
        
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
            
        if orientation == Qt.Orientation.Horizontal:
            headers = ["#", "★", "", "Name", "Channels", "Format", "Duration", "Waveform"]
            if 0 <= section < len(headers):
                return headers[section]
        return None

    def set_playing_index(self, index_row):
        old_idx = self._playing_index
        self._playing_index = index_row
        
        # Refresh old and new rows
        if old_idx != -1:
            self.dataChanged.emit(self.index(old_idx, 0), self.index(old_idx, self.COL_COUNT-1))
        if index_row != -1:
            self.dataChanged.emit(self.index(index_row, 0), self.index(index_row, self.COL_COUNT-1))
            
    def get_track_at(self, row):
        if 0 <= row < len(self._tracks):
            return self._tracks[row]
        return None

    def clear(self):
        self.beginResetModel()
        self._tracks = []
        self._playing_index = -1
        self.endResetModel()

    def remove_track_by_path(self, path):
        # Find index
        norm_path = os.path.normpath(path)
        for i, track in enumerate(self._tracks):
            if os.path.normpath(track.get("path", "")) == norm_path:
                self.beginRemoveRows(QModelIndex(), i, i)
                self._tracks.pop(i)
                
                # Adjust playing index
                if self._playing_index == i:
                    self._playing_index = -1
                elif self._playing_index > i:
                    self._playing_index -= 1
                    
                self.endRemoveRows()
                return True
        return False

    def flags(self, index):
        return super().flags(index)
