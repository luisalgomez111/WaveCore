from PyQt6.QtCore import pyqtSignal, Qt, QUrl, QSize
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QSlider, QLabel, QStyle, QFrame)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtGui import QIcon, QPixmap
import os

class VideoPlayerWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Resources for icons
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.icons_dir = os.path.join(self.base_dir, "resources", "icons")
        
        # Media Player Setup
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        
        self.init_ui()
        
        # Signals
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.playbackStateChanged.connect(self.media_state_changed)
        self.media_player.errorOccurred.connect(self.handle_errors)
        
        # Internal State
        self.duration = 0
        self.is_slider_dragging = False

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Video Area
        self.video_widget.setStyleSheet("background-color: black;")
        self.main_layout.addWidget(self.video_widget, 1)
        
        # Custom Playback Bar
        self.controls_container = QFrame()
        self.controls_container.setFixedHeight(60)
        self.controls_container.setFixedHeight(60)
        self.controls_container.setStyleSheet("""
            QFrame { background-color: #000000; border: none; }
        """)
        self.controls_layout = QHBoxLayout(self.controls_container)
        self.controls_layout.setContentsMargins(20, 0, 20, 0)
        self.controls_layout.setSpacing(20)
        
        # Play Button
        self.btn_play = QPushButton()
        self.btn_play.setFixedSize(40, 40)
        self.btn_play.setIconSize(pd_size := QSize(24, 24))
        self.btn_play.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_play.setIcon(QIcon(os.path.join(self.icons_dir, "play.svg")))
        self.btn_play.clicked.connect(self.play_video)
        self.controls_layout.addWidget(self.btn_play)
        
        # Pause Button
        self.btn_pause = QPushButton()
        self.btn_pause.setFixedSize(40, 40)
        self.btn_pause.setIconSize(pd_size)
        self.btn_pause.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_pause.setIcon(QIcon(os.path.join(self.icons_dir, "pause.svg")))
        self.btn_pause.clicked.connect(self.pause_video)
        self.controls_layout.addWidget(self.btn_pause)
        
        # Style for Buttons
        ctrl_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #333;
            }
            QPushButton:disabled {
                opacity: 0.5;
            }
        """
        self.btn_play.setStyleSheet(ctrl_style)
        self.btn_pause.setStyleSheet(ctrl_style)
        
        # Initially Disabled
        self.btn_play.setEnabled(False)
        self.btn_pause.setEnabled(False)
        
        # Time Label
        self.time_lbl = QLabel("00:00 / 00:00")
        self.time_lbl.setStyleSheet("color: #888; font-family: 'Segoe UI', sans-serif; font-size: 12px; border: none; background: transparent;")
        self.controls_layout.addWidget(self.time_lbl)
        
        # Timeline Slider (Replaces Waveform)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: #333;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #D75239;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ddd;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #fff;
            }
        """)
        self.slider.sliderMoved.connect(self.set_position)
        self.slider.sliderPressed.connect(self.slider_pressed)
        self.slider.sliderReleased.connect(self.slider_released)
        self.controls_layout.addWidget(self.slider)
        
        # Volume Icon & Slider
        vol_icon = QLabel()
        vol_pix = QIcon(os.path.join(self.icons_dir, "volume.svg")).pixmap(16, 16)
        if not vol_pix.isNull():
            vol_icon.setPixmap(vol_pix)
        else:
            vol_icon.setText("VOL")
            vol_icon.setStyleSheet("color: #888;")
        self.controls_layout.addWidget(vol_icon)

        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(70)
        self.vol_slider.setFixedWidth(80)
        self.vol_slider.setStyleSheet("""
            QSlider::groove:horizontal {
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
        """)
        self.vol_slider.valueChanged.connect(self.set_volume)
        self.controls_layout.addWidget(self.vol_slider)
        
        self.main_layout.addWidget(self.controls_container)

    def load_video(self, path):
        # Stop current before loading new
        self.media_player.stop()
        self.media_player.setSource(QUrl.fromLocalFile(path))
        self.btn_play.setEnabled(True)
        self.btn_pause.setEnabled(True)
        self.btn_play.setFocus()
        
    def play_video(self):
        self.media_player.play()

    def apply_theme(self, t):
        self.controls_container.setStyleSheet(f"""
            QFrame {{ background-color: {t.get("bg_secondary")}; border-top: 1px solid {t.get("border")}; }}
        """)
        
        btn_style = f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {t.get("bg_button")};
            }}
        """
        self.btn_play.setStyleSheet(btn_style)
        self.btn_pause.setStyleSheet(btn_style)
        
        self.time_lbl.setStyleSheet(f"color: {t.get('text_secondary')}; font-family: 'Segoe UI', sans-serif; font-size: 12px; border: none; background: transparent;")
        
        slider_style = f"""
            QSlider::groove:horizontal {{
                height: 4px;
                background: {t.get("bg_button")};
                border-radius: 2px;
            }}
            QSlider::sub-page:horizontal {{
                background: {t.get("accent")};
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {t.get("text_main")};
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }}
        """
        self.slider.setStyleSheet(slider_style)
        self.vol_slider.setStyleSheet(slider_style)

    def pause_video(self):
        self.media_player.pause()

    def media_state_changed(self, state):
        pass

    def position_changed(self, position):
        if not self.is_slider_dragging:
            self.slider.setValue(position)
        self.update_time_label(position)

    def duration_changed(self, duration):
        self.duration = duration
        self.slider.setRange(0, duration)
        self.update_time_label(self.media_player.position())

    def set_position(self, position):
        self.media_player.setPosition(position)
        self.update_time_label(position)

    def slider_pressed(self):
        self.is_slider_dragging = True

    def slider_released(self):
        self.is_slider_dragging = False
        self.media_player.setPosition(self.slider.value())

    def set_volume(self, volume):
        # QAudioOutput volume is 0.0 to 1.0
        self.audio_output.setVolume(volume / 100.0)

    def update_time_label(self, current_ms):
        def fmt(ms):
            seconds = (ms // 1000) % 60
            minutes = (ms // 60000) % 60
            return f"{minutes:02}:{seconds:02}"
        self.time_lbl.setText(f"{fmt(current_ms)} / {fmt(self.duration)}")
        
    def handle_errors(self):
        self.btn_play.setEnabled(False)
        self.btn_pause.setEnabled(False)
        print(f"Video Player Error: {self.media_player.errorString()}")
