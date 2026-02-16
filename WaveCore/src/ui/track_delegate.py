from PyQt6.QtWidgets import QStyledItemDelegate, QStyle
from PyQt6 import QtCore, QtGui
import math
import numpy as np
from ui.library_model import LibraryModel
from constants import LibraryColumns

class TrackDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Default Colors (Dark)
        self.text_color = QtGui.QColor("#cccccc")
        self.text_dim = QtGui.QColor("#888888")
        self.text_highlight = QtGui.QColor("#D75239")
        self.bg_selected = QtGui.QColor("#2a2a2a")
        self.bg_hover = QtGui.QColor("#1a1a1a")
        
    def apply_theme(self, t):
        self.text_color = QtGui.QColor(t.get("text_main"))
        self.text_dim = QtGui.QColor(t.get("text_secondary"))
        self.text_highlight = QtGui.QColor(t.get("accent"))
        self.bg_selected = QtGui.QColor(t.get("bg_button"))
        self.bg_hover = QtGui.QColor(t.get("bg_toolbar"))
        
    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        # Background
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, self.bg_selected)
        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(option.rect, self.bg_hover)
            
        # Data
        track = index.data(QtCore.Qt.ItemDataRole.UserRole)
        col = index.column()
        rect = option.rect
        
        # Determine Color
        color = self.text_color
        if option.state & QStyle.StateFlag.State_Selected:
            color = self.text_highlight
            
        painter.setPen(color)
        
        # 1. Index
        if col == LibraryModel.COL_INDEX:
            painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter, str(index.row() + 1) + " ")
            
        # 1b. Favorites (Star)
        elif col == LibraryModel.COL_FAV:
            is_fav = index.data(QtCore.Qt.ItemDataRole.UserRole + 2) # Role for Fav
            cx, cy = rect.center().x(), rect.center().y()
            
            if is_fav:
                path = QtGui.QPainterPath()
                # Draw geometric star
                points = []
                for i in range(10):
                    angle = -math.pi/2 + i * math.pi/5
                    r = 8 if i % 2 == 0 else 3.5
                    points.append(QtCore.QPoint(int(cx + r * math.cos(angle)), int(cy + r * math.sin(angle))))
                
                path.moveTo(points[0].x(), points[0].y())
                for p in points[1:]:
                    path.lineTo(p.x(), p.y())
                path.closeSubpath()
                
                # Premium Gold Gradient
                grad = QtGui.QLinearGradient(cx, cy - 8, cx, cy + 8)
                grad.setColorAt(0, QtGui.QColor("#FFE082")) # Light Gold
                grad.setColorAt(0.5, QtGui.QColor("#FFD700")) # Main Gold
                grad.setColorAt(1, QtGui.QColor("#FF8C00")) # Deep Gold/Orange
                
                painter.setPen(QtGui.QPen(QtGui.QColor("#403000"), 1)) # Dark thin outline
                painter.setBrush(QtGui.QBrush(grad))
                painter.drawPath(path)
            else:
                # Dim placeholder star (hollow)
                painter.setPen(QtGui.QPen(self.text_dim, 1))
                painter.setBrush(QtCore.Qt.GlobalColor.transparent)
                painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, "☆")

        # 2. Play Button / Icon
        elif col == LibraryModel.COL_PLAY:
            # Draw Simple Play Triangle
            # Center it
            cx, cy = rect.center().x(), rect.center().y()
            size = 10
            # If playing (checked via model?) -> Pause icon?
            # For now simplified: always Play icon, interactive
            painter.setBrush(QtGui.QBrush(color))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            
            # Triangle
            painter.drawPolygon([
                QtCore.QPoint(cx - 4, cy - 6),
                QtCore.QPoint(cx - 4, cy + 6),
                QtCore.QPoint(cx + 6, cy)
            ])
            
        # 3. Waveform
        elif col == LibraryModel.COL_WAVEFORM:
            if track:
                self._draw_waveform_cached(painter, rect, track, color)
        
        # 4. Text Columns
        else:
            text = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
            # Adjust color for specific cols
            if col in (LibraryModel.COL_FORMAT, LibraryModel.COL_DURATION, LibraryModel.COL_CHANNELS):
                painter.setPen(self.text_dim)
                
            align = QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter
            if col == LibraryModel.COL_INDEX:
                align = QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
            elif col in (LibraryModel.COL_FORMAT, LibraryModel.COL_CHANNELS, LibraryModel.COL_DURATION):
                align = QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignVCenter
                
            # Padding
            r = QtCore.QRect(rect)
            r.adjust(5, 0, -5, 0)
            painter.drawText(r, align, str(text))
            
        painter.restore()
        
    def _draw_waveform(self, painter, rect, data, color):
        if data is None or len(data) == 0: return
        
        # Check Cache in track data
        # We need the track dict to store the cache
        # We'll use a hidden key in the track dict
        # We must verify width/height match to reuse
        width = rect.width()
        height = rect.height()
        
        # Since 'data' is passed from 'track.get("waveform")', 
        # let's assume the caller can help us find the track dict
        # Actually, let's just use a simple cache on the 'data' object itself or nearby
        # Better: the track dict is available in paint()
        
        # NOTE: This method is called with 'data', not 'track'. 
        # To optimize, I'll modify the caller in paint()
        pass

    def _get_cached_waveform_path(self, track_dict, width, height, color_hex):
        cache = track_dict.get("_wave_path_cache")
        if cache and cache["w"] == width and cache["h"] == height and cache["color"] == color_hex:
            return cache["path"]
        return None

    def _draw_waveform_cached(self, painter, rect, track_dict, color):
        data = track_dict.get("waveform")
        if data is None or len(data) == 0: return
        
        width = rect.width()
        height = rect.height()
        color_hex = color.name()
        
        path = self._get_cached_waveform_path(track_dict, width, height, color_hex)
        
        if path is None:
            path = QtGui.QPainterPath()
            # Path is relative: x=0 to width, y=0 is the center line
            mid_y_local = 0 
            max_h = height * 0.8
            
            # Spotify style: Discrete Bars
            bar_w = 1.5 
            gap = 1.0
            step_px = bar_w + gap
            
            for x_rel in np.arange(0, float(width), float(step_px)):
                data_ratio = x_rel / width
                idx = int(data_ratio * len(data))
                if idx >= len(data): break
                
                val = abs(data[idx])
                h = max(2, val * max_h)
                
                # Add bar relative to (0,0) center
                path.addRoundedRect(float(x_rel), float(-h/2), float(bar_w), float(h), 0.7, 0.7)
            
            track_dict["_wave_path_cache"] = {
                "w": width, "h": height, "color": color_hex, "path": path
            }
            
        painter.save()
        # Translate to the center-left of the target rect
        painter.translate(rect.x(), rect.center().y())
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.fillPath(path, QtGui.QBrush(color))
        painter.restore()

