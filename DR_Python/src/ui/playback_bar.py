from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QSlider, QGraphicsDropShadowEffect, QSizePolicy, QApplication
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QMimeData, QUrl, QPoint
from PyQt6.QtGui import QIcon, QColor, QDrag, QPixmap
import os
from ui.waveform_widget import WaveformWidget

class PlaybackBar(QWidget):
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    speed_changed = pyqtSignal(float)
    seek_requested = pyqtSignal(float)
    volume_changed = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PlaybackBar")
        self.setMinimumHeight(120) 
        self.current_track_path = None
        
        # Shadow Effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(-5)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet("""
            #PlaybackBar { background-color: #181818; border-top: 1px solid #2a2a2a; }
            
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #2a2a2a; }
            
            /* Labels */
            QLabel { color: #b3b3b3; font-family: 'Segoe UI', sans-serif; font-size: 12px; border: none; }
            QLabel#track_title { color: #ffffff; font-weight: bold; font-size: 13px; }
            QLabel#time { font-family: 'Consolas', monospace; color: #a0a0a0; }
            
            /* Sliders */
            QSlider::groove:horizontal {
                border: 1px solid #3d3d3d;
                height: 4px;
                background: #404040;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #D75239;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                width: 10px;
                height: 10px;
                margin: -3px 0; 
                border-radius: 5px;
            }
            QSlider::handle:horizontal:hover {
                background-color: #f0f0f0;
            }
            
            /* Circle Buttons Hover */
            QPushButton#btn_play:hover, QPushButton#btn_pause:hover, QPushButton#btn_drag:hover {
                background-color: #333333;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5) 
        layout.setSpacing(0) 
        
        # Load Icons
        base_path = os.path.dirname(os.path.dirname(__file__)) # src/
        icon_path = os.path.join(base_path, 'resources', 'icons')
        
        icon_play = QIcon(os.path.join(icon_path, 'play.svg'))
        icon_pause = QIcon(os.path.join(icon_path, 'pause.svg'))
        icon_vol = QIcon(os.path.join(icon_path, 'volume.svg'))
        icon_drag = QIcon(os.path.join(icon_path, 'drag.svg'))
        
        # --- TOP ROW ---
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 5) 
        
        # 1. Track Info (Left)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        self.lbl_title = QLabel("Select a track")
        self.lbl_title.setObjectName("track_title")
        info_layout.addWidget(self.lbl_title)
        top_layout.addLayout(info_layout, 1) 
        
        # 2. Player Controls (Center)
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(10)
        ctrl_layout.addStretch()
        
        self.btn_speed = QPushButton("1.0x")
        self.btn_speed.setFixedSize(40, 24)
        self.btn_speed.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_speed.setStyleSheet("color: #888888; border: 1px solid #444; border-radius: 12px; font-size: 10px;")
        self.btn_speed.clicked.connect(self.toggle_speed)
        self.current_speed_idx = 0
        self.speeds = [0.5, 1.0, 1.5, 2.0]
        ctrl_layout.addWidget(self.btn_speed)
        
        # --- DRAG BUTTON ---
        self.btn_drag = QPushButton()
        self.btn_drag.setObjectName("btn_drag")
        self.btn_drag.setIcon(icon_drag)
        self.btn_drag.setIconSize(QSize(22, 22))
        self.btn_drag.setFixedSize(40, 40)
        self.btn_drag.setToolTip("Drag full track")
        self.btn_drag.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_drag.setCursor(Qt.CursorShape.OpenHandCursor)
        # We handle the drag via mouse move oversight or custom event
        self.btn_drag.mousePressEvent = self._on_drag_press
        self.btn_drag.mouseMoveEvent = self._on_drag_move
        ctrl_layout.addWidget(self.btn_drag)
        
        self.btn_play = QPushButton()
        self.btn_play.setIcon(icon_play)
        self.btn_play.setIconSize(QSize(24, 24))
        self.btn_play.setFixedSize(40, 40)
        self.btn_play.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_play.clicked.connect(self.play_clicked.emit)
        ctrl_layout.addWidget(self.btn_play)
        
        self.btn_pause = QPushButton()
        self.btn_pause.setIcon(icon_pause)
        self.btn_pause.setIconSize(QSize(24, 24))
        self.btn_pause.setFixedSize(40, 40)
        self.btn_pause.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_pause.clicked.connect(self.pause_clicked.emit)
        ctrl_layout.addWidget(self.btn_pause)
        
        ctrl_layout.addStretch()
        top_layout.addLayout(ctrl_layout, 2) 
        
        # 3. Volume & Time (Right)
        right_layout = QHBoxLayout()
        right_layout.setSpacing(10)
        
        self.lbl_time = QLabel("00:00 / 00:00")
        self.lbl_time.setObjectName("time")
        right_layout.addWidget(self.lbl_time)
        
        lbl_vol = QLabel()
        lbl_vol.setPixmap(icon_vol.pixmap(16, 16))
        right_layout.addWidget(lbl_vol)
        
        self.slider_vol = QSlider(Qt.Orientation.Horizontal)
        self.slider_vol.setRange(0, 100)
        self.slider_vol.setValue(80)
        self.slider_vol.setFixedWidth(80)
        self.slider_vol.valueChanged.connect(lambda v: self.volume_changed.emit(v / 100.0))
        right_layout.addWidget(self.slider_vol)
        
        top_layout.addLayout(right_layout, 1) 
        
        layout.addLayout(top_layout, 0)
        
        # --- WAVEFORM (Bottom) ---
        self.waveform = WaveformWidget()
        self.waveform.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.waveform.setMinimumHeight(40) 
        self.waveform.bg_color = QColor(Qt.GlobalColor.transparent) 
        self.waveform.set_colors("#555555", "#D75239")
        self.waveform.seek_requested.connect(self.seek_requested.emit)
        
        layout.addWidget(self.waveform, 1)
        
    def _on_drag_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.pos()
            self.btn_drag.setCursor(Qt.CursorShape.ClosedHandCursor)

    def _on_drag_move(self, event):
        if not self.current_track_path: return
        if not (event.buttons() & Qt.MouseButton.LeftButton): return
        
        if (event.pos() - self._drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return
            
        drag = QDrag(self)
        mime = QMimeData()
        url = QUrl.fromLocalFile(self.current_track_path)
        mime.setUrls([url])
        drag.setMimeData(mime)
        
        # Pixmap for drag feedback
        pixmap = self.btn_drag.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        
        self.btn_drag.setCursor(Qt.CursorShape.OpenHandCursor)
        drag.exec(Qt.DropAction.CopyAction)

    def toggle_speed(self):
        self.current_speed_idx = (self.current_speed_idx + 1) % len(self.speeds)
        speed = self.speeds[self.current_speed_idx]
        self.btn_speed.setText(f"{speed}x")
        self.speed_changed.emit(speed)

    def set_track_info(self, title, data, path=None, duration=0):
        self.lbl_title.setText(title)
        self.current_track_path = path
        self.waveform.set_data(data, path, duration)
        self.waveform.set_progress(0)
        self.set_playing_state(False)
        
    def update_progress(self, current_ms, total_ms):
        if total_ms > 0:
            ratio = current_ms / total_ms
            self.waveform.set_progress(ratio)
            curr_s = int(current_ms / 1000)
            tot_s = int(total_ms / 1000)
            self.lbl_time.setText(f"{curr_s//60:02d}:{curr_s%60:02d} / {tot_s//60:02d}:{tot_s%60:02d}")

    def set_playing_state(self, is_playing):
        if is_playing:
            self.btn_play.setStyleSheet("background-color: transparent;")
            self.btn_pause.setStyleSheet("background-color: transparent;") 
        else:
            self.btn_play.setStyleSheet("background-color: transparent;") 
            self.btn_pause.setStyleSheet("background-color: transparent;")


