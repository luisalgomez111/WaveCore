from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QUrl

class OnlineTrackRow(QWidget):
    def __init__(self, index, name, duration, description, parent=None):
        super().__init__(parent)
        
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
            QLabel#duration { color: #D75239; font-family: Consolas; font-size: 12px; }
            QLabel#desc { color: #999999; font-size: 12px; font-style: italic; }
            
            QPushButton#download_btn {
                background-color: #333;
                color: white;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton#download_btn:hover { background-color: #D75239; }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        def add_row_lbl(text, width=None, align=Qt.AlignmentFlag.AlignLeft, expand=False, obj_name=None):
            lbl = QLabel(text)
            lbl.setContentsMargins(5, 0, 5, 0)
            if width: lbl.setFixedWidth(width)
            if obj_name: lbl.setObjectName(obj_name)
            lbl.setAlignment(align | Qt.AlignmentFlag.AlignVCenter)
            if expand: layout.addWidget(lbl, 1)
            else: layout.addWidget(lbl)
            return lbl

        # 1. Index (40px)
        add_row_lbl(str(index), 40, Qt.AlignmentFlag.AlignRight, obj_name="index")
        
        # 2. Play Icon (25px)
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(25, 25)
        self.play_btn.setContentsMargins(0,0,0,0)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.play_btn)
        
        # 3. Name (200px)
        self.name_lbl = add_row_lbl(name, 200)
        self.name_lbl.setToolTip(name)
        
        # 4. Format/Type (60px)
        self.fmt_lbl = add_row_lbl("MP3", 60, Qt.AlignmentFlag.AlignCenter)
        
        # 5. Duration (70px)
        mins = int(duration // 60)
        secs = int(duration % 60)
        self.duration_lbl = add_row_lbl(f"{mins:02d}:{secs:02d}", 70, Qt.AlignmentFlag.AlignRight, obj_name="duration")
        
        # 6. Description/Tags (150px)
        self.desc_lbl = add_row_lbl(description, 150, obj_name="desc")
        
        # 7. Action Button
        action_container = QWidget()
        ac_layout = QHBoxLayout(action_container)
        ac_layout.setContentsMargins(5, 0, 5, 0)
        ac_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.download_btn = QPushButton("DOWNLOAD")
        self.download_btn.setObjectName("download_btn")
        self.download_btn.setFixedSize(80, 24)
        ac_layout.addWidget(self.download_btn)
        layout.addWidget(action_container) # Removed stretch factor (1)

        # 8. Main layout stretch to push everything left
        layout.addStretch()

        # 9. Spacer for scrollbar alignment with header
        row_spacer = QWidget()
        row_spacer.setFixedWidth(15)
        layout.addWidget(row_spacer)
