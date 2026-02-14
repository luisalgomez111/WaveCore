from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QDrag, QPixmap, QPainterPath, QLinearGradient
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QRect, QRectF, pyqtSignal, QMimeData, QUrl, QPoint, QTimer
import numpy as np

class WaveformWidget(QWidget):
    seek_requested = pyqtSignal(float) # 0.0 to 1.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = None
        self.file_path = None
        self.duration_sec = 0
        
        self.bg_color = QColor("#262626")
        self.wave_color = QColor("#525252") 
        self.progress_color = QColor("#D75239") 
        self.selection_color = QColor(0, 120, 215, 100)
        self.selection_border = QColor(0, 120, 215, 200)
        self.playhead_color = QColor("#FFFFFF")
        
        self.progress = 0.0 # Target progress from player
        self.display_progress = 0.0 # Interpolated progress for drawing
        self.sel_start = None
        self.sel_end = None
        
        self.is_selecting = False
        self.is_scrubbing = False
        self.is_panning = False
        self.start_x = 0
        
        self.zoom_factor = 1.0 # 1.0 = no zoom
        self.view_offset = 0.0 # Left side of visible window (0.0 to 1.0)
        
        # Caching
        self._pixmap_base = None
        self._pixmap_progress = None
        self._cached_width = -1
        self._cached_height = -1
        self._cached_zoom = -1
        self._cached_offset = -1
        
        # Animation Timer (Smooth interpolation)
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(16) # ~60 FPS
        self.anim_timer.timeout.connect(self._on_anim_tick)
        self.anim_timer.start()

        self.setMinimumHeight(40)
        self.setMouseTracking(True)

    def _on_anim_tick(self):
        # Smoothly interpolate display_progress towards progress
        diff = self.progress - self.display_progress
        if abs(diff) < 0.0001:
            if self.display_progress != self.progress:
                self.display_progress = self.progress
                self.update()
            return
            
        # Adjust speed: 0.2 means it moves 20% of the distance every 16ms
        step = diff * 0.3 
        self.display_progress += step
        self.update()

    def set_data(self, data, file_path=None, duration=0):
        self.data = data
        self.file_path = file_path
        self.duration_sec = duration
        self.sel_start = None
        self.sel_end = None
        self.zoom_factor = 1.0
        self.view_offset = 0.0
        self._pixmap_base = None # Invalidate cache
        self._pixmap_progress = None
        self.update()

    def set_progress(self, progress):
        self.progress = progress
        # If jumping significantly (user seek), snap display_progress
        if abs(self.progress - self.display_progress) > 0.1:
            self.display_progress = self.progress
        self.update()
        
    def set_colors(self, wave, progress):
        self.wave_color = QColor(wave)
        self.progress_color = QColor(progress)
        self._pixmap_base = None
        self._pixmap_progress = None
        self.update()

    def _render_pixmaps(self, width, height):
        if (self._pixmap_base and width == self._cached_width and 
            height == self._cached_height and self.zoom_factor == self._cached_zoom and
            self.view_offset == self._cached_offset):
            return
            
        if self.data is None or len(self.data) == 0:
            return
            
        # Create new pixmaps
        self._pixmap_base = QPixmap(width, height)
        self._pixmap_base.fill(Qt.GlobalColor.transparent)
        
        self._pixmap_progress = QPixmap(width, height)
        self._pixmap_progress.fill(Qt.GlobalColor.transparent)
        
        p_base = QPainter(self._pixmap_base)
        p_prog = QPainter(self._pixmap_progress)
        
        for p in [p_base, p_prog]:
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            
        mid_y = height / 2
        max_h = height * 0.85
        
        # Spotify style: Discrete Bars
        bar_w = 2 
        gap = 1
        step_px = bar_w + gap
        
        # Window into data
        start_idx = int(self.view_offset * len(self.data))
        win_len = int(len(self.data) / self.zoom_factor)
        end_idx = min(start_idx + win_len, len(self.data))
        
        win_data = self.data[start_idx:end_idx]
        if len(win_data) < 2: 
            p_base.end()
            p_prog.end()
            return

        # Progress Gradient for the progress pixmap
        grad = QLinearGradient(0, 0, 0, height)
        grad.setColorAt(0, self.progress_color.lighter(110))
        grad.setColorAt(0.5, self.progress_color)
        grad.setColorAt(1, self.progress_color.darker(110))
        
        p_base.setBrush(QBrush(self.wave_color))
        p_base.setPen(Qt.PenStyle.NoPen)
        
        p_prog.setBrush(QBrush(grad))
        p_prog.setPen(Qt.PenStyle.NoPen)
        
        # Draw Bars
        for x in range(0, width, step_px):
            data_ratio = x / width
            idx = int(data_ratio * len(win_data))
            if idx >= len(win_data): break
            
            val = abs(win_data[idx])
            h = max(2, val * max_h)
            
            # Draw to both pixmaps
            rect_f = QtCore.QRectF(float(x), float(mid_y - h/2), float(bar_w), float(h))
            p_base.drawRoundedRect(rect_f, 1.0, 1.0)
            p_prog.drawRoundedRect(rect_f, 1.0, 1.0)
            
        p_base.end()
        p_prog.end()
        
        self._cached_width = width
        self._cached_height = height
        self._cached_zoom = self.zoom_factor
        self._cached_offset = self.view_offset

    def _map_to_view(self, val):
        return (val - self.view_offset) * self.zoom_factor

    def _map_from_view(self, view_x_ratio):
        return self.view_offset + view_x_ratio / self.zoom_factor

    def paintEvent(self, event):
        painter = QPainter(self)
        
        width = self.width()
        height = self.height()
        
        # 1. Background
        painter.fillRect(self.rect(), self.bg_color)
        
        if self.data is None: return
        
        # 2. Render/Get Pixmaps
        self._render_pixmaps(width, height)
        if not self._pixmap_base: return
            
        progress_view = self._map_to_view(self.display_progress)
        split_x = int(width * progress_view)
        
        # 3. Draw Waveform (Remaining/Base part)
        painter.save()
        if split_x < width:
            painter.setClipRect(max(0, split_x), 0, width - max(0, split_x), height)
            painter.drawPixmap(0, 0, self._pixmap_base)
        painter.restore()
        
        # 4. Draw Waveform (Played part)
        if split_x > 0:
            painter.save()
            painter.setClipRect(0, 0, min(width, split_x), height)
            painter.drawPixmap(0, 0, self._pixmap_progress)
            painter.restore()
            
        # 4. Selection
        if self.sel_start is not None and self.sel_end is not None:
             s, e = sorted((self.sel_start, self.sel_end))
             sv = self._map_to_view(s)
             ev = self._map_to_view(e)
             sx, ex = int(sv * width), int(ev * width)
             sw = ex - sx
             if sw > 0:
                 painter.setBrush(QBrush(QColor(self.selection_color)))
                 painter.setPen(QPen(self.selection_border, 1))
                 painter.drawRect(sx, 0, sw, height)

        # 5. Playhead indicator
        if 0 <= progress_view <= 1.0:
            painter.setPen(QPen(self.playhead_color, 1))
            painter.drawLine(split_x, 0, split_x, height)
            painter.setBrush(QBrush(self.playhead_color))
            painter.setPen(Qt.PenStyle.NoPen)
            points = [QPoint(split_x-5, 0), QPoint(split_x+5, 0), QPoint(split_x, 8)]
            painter.drawPolygon(points)

    # ... Rest of interaction methods (mousePress/Move/Release/etc) ...
    def mousePressEvent(self, event):
        x = event.pos().x()
        w = self.width()
        val = self._map_from_view(x / w) if w > 0 else 0
        
        if event.button() == Qt.MouseButton.RightButton:
            self.is_panning = True
            self.last_pan_x = x
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            ph_view = self._map_to_view(self.progress)
            ph_x = ph_view * w
            if abs(x - ph_x) < 8:
                self.is_scrubbing = True
                self.setCursor(Qt.CursorShape.SizeHorCursor)
                return
            if self._is_inside_selection(val):
                self.is_selecting = False 
                self.is_scrubbing = False
                self.drag_start_pos = event.pos()
            else:
                self.is_selecting = True
                self.sel_start = val
                self.sel_end = val
                self.start_x = x
                self.seek_requested.emit(val)
                self.set_progress(val)
            self.update()

    def mouseMoveEvent(self, event):
        x = event.pos().x()
        w = self.width()
        val = self._map_from_view(x / w) if w > 0 else 0
        
        if self.is_panning:
            diff_x = x - self.last_pan_x
            self.last_pan_x = x
            # Distance in track units
            dist = (diff_x / w) / self.zoom_factor
            self.view_offset -= dist
            self.view_offset = max(0.0, min(self.view_offset, 1.0 - 1.0/self.zoom_factor))
            self._pixmap_base = None
            self.update()
            return

        ph_view = self._map_to_view(self.progress)
        ph_x = ph_view * w
        if not self.is_scrubbing and not self.is_selecting:
             if abs(x - ph_x) < 8:
                 self.setCursor(Qt.CursorShape.SizeHorCursor)
             elif self._is_inside_selection(val):
                 self.setCursor(Qt.CursorShape.OpenHandCursor)
             else:
                 self.setCursor(Qt.CursorShape.IBeamCursor)
        
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.is_scrubbing:
                self.seek_requested.emit(val)
                self.set_progress(val)
            elif self.is_selecting:
                self.sel_end = val
                self.update()
            elif self.sel_start is not None and self.sel_end is not None:
                if hasattr(self, 'drag_start_pos') and (event.pos() - self.drag_start_pos).manhattanLength() > QApplication.startDragDistance():
                     self.start_drag()
        
    def mouseReleaseEvent(self, event):
        if self.is_panning:
            self.is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_scrubbing:
                self.is_scrubbing = False
                self.setCursor(Qt.CursorShape.ArrowCursor)
            elif self.is_selecting:
                start = min(self.sel_start, self.sel_end)
                end = max(self.sel_start, self.sel_end)
                if abs(end - start) < 0.001:
                    self.sel_start = None
                    self.sel_end = None
                else:
                    self.sel_start = start
                    self.sel_end = end
            self.is_selecting = False
            self.update()

    def wheelEvent(self, event):
        if self.data is None: return
        
        delta = event.angleDelta().y()
        mouse_x = event.position().x()
        w = self.width()
        if w == 0: return

        # Relative pos in track (0.0 to 1.0)
        mouse_rel = self.view_offset + (mouse_x / w) / self.zoom_factor
        
        zoom_step = 1.25
        if delta > 0:
            self.zoom_factor *= zoom_step
        else:
            self.zoom_factor /= zoom_step
            
        self.zoom_factor = max(1.0, min(self.zoom_factor, 100.0))
        
        # Adjust view_offset to keep mouse_rel persistent
        self.view_offset = mouse_rel - (mouse_x / w) / self.zoom_factor
        self.view_offset = max(0.0, min(self.view_offset, 1.0 - 1.0/self.zoom_factor))
        
        self._pixmap_base = None
        self.update()

    def _is_inside_selection(self, val):
        if self.sel_start is None or self.sel_end is None: return False
        s, e = sorted((self.sel_start, self.sel_end))
        return s <= val <= e

    def start_drag(self):
        if not self.file_path or self.sel_start is None: return
        s, e = sorted((self.sel_start, self.sel_end))
        start_ms = s * self.duration_sec * 1000
        end_ms = e * self.duration_sec * 1000
        from utils.audio_exporter import export_snippet
        snippet_path = export_snippet(self.file_path, start_ms, end_ms)
        if snippet_path:
            drag = QDrag(self)
            mime = QMimeData()
            url = QUrl.fromLocalFile(snippet_path)
            mime.setUrls([url])
            mime.setText(f"Snippet from {self.file_path}")
            drag.setMimeData(mime)
            drag.setPixmap(self._create_drag_pixmap())
            drag.setHotSpot(QPoint(10, 10))
            drag.exec(Qt.DropAction.CopyAction)

    def _create_drag_pixmap(self):
        pixmap = QPixmap(100, 40)
        pixmap.fill(QColor(0, 0, 0, 100))
        painter = QPainter(pixmap)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.progress_color)
        painter.drawRect(0, 10, 100, 20)
        painter.end()
        return pixmap
