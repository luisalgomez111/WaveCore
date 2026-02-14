from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from ui.waveform_widget import WaveformWidget

class TrackRow(QWidget):
    def __init__(self, index, file_path, file_name, file_ext, duration, description="", parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.duration = duration
        
        # Soundly Style: Compact Row (~30-45px)
        self.setFixedHeight(45)
        self.setStyleSheet("""
            QWidget { background-color: transparent; }
            QLabel { color: #cccccc; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
            QPushButton { 
                background-color: transparent; 
                border: none; 
                color: #aaaaaa; 
                font-size: 14px; 
            }
            QPushButton:hover { color: #D75239; }
            
            /* Specific Column Styles */
            QLabel#index { color: #666666; font-size: 11px; }
            QLabel#format { color: #888888; font-size: 11px; font-weight: bold; }
            QLabel#duration { color: #D75239; font-family: Consolas; font-size: 12px; }
            QLabel#desc { color: #999999; font-size: 12px; font-style: italic; }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)
        
        # 1. Index (40px)
        self.idx_lbl = QLabel(str(index))
        self.idx_lbl.setObjectName("index")
        self.idx_lbl.setFixedWidth(40)
        self.idx_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.idx_lbl)
        
        # 2. Pseudo-Play Icon (Small)
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(25, 25)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.play_btn)
        
        # 3. Filename (200px)
        self.name_lbl = QLabel(file_name)
        self.name_lbl.setFixedWidth(200) 
        self.name_lbl.setToolTip(file_name)
        layout.addWidget(self.name_lbl)
        
        # 4. Format (60px)
        self.fmt_lbl = QLabel(file_ext.upper().replace(".", ""))
        self.fmt_lbl.setObjectName("format")
        self.fmt_lbl.setFixedWidth(60)
        self.fmt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.fmt_lbl)

        # 5. Duration (70px)
        mins = int(duration // 60)
        secs = int(duration % 60)
        self.duration_lbl = QLabel(f"{mins:02d}:{secs:02d}")
        self.duration_lbl.setObjectName("duration")
        self.duration_lbl.setFixedWidth(70)
        self.duration_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.duration_lbl)
        
        # 6. Description (150px)
        self.desc_lbl = QLabel(description if description else "-")
        self.desc_lbl.setObjectName("desc")
        self.desc_lbl.setFixedWidth(150)
        layout.addWidget(self.desc_lbl)
        
        # 7. Waveform (Takes all remaining space)
        self.waveform = WaveformWidget()
        self.waveform.bg_color = Qt.GlobalColor.transparent 
        self.waveform.wave_color = "#555555"
        self.waveform.progress_color = "#D75239"
        self.waveform.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.waveform, 1)
        
    def set_waveform_data(self, data):
        self.waveform.set_data(data)
