from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QButtonGroup
from PyQt6.QtCore import pyqtSignal, QSize, Qt
from PyQt6.QtGui import QIcon

class BottomBar(QWidget):
    module_changed = pyqtSignal(int)
    
    def __init__(self, localizer=None):
        super().__init__()
        self.localizer = localizer
        self.setFixedHeight(50)
        self.setObjectName("bottomBar")
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        self.btn_group.idClicked.connect(self.on_btn_clicked)
        
        self.init_buttons()

    def apply_theme(self, t):
        self.setStyleSheet(f"""
            QWidget#bottomBar {{
                background-color: {t.get("bg_secondary")};
                border-top: 1px solid {t.get("border")};
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {t.get("text_secondary")};
                font-family: 'Segoe UI', sans-serif;
                font-weight: bold;
                font-size: 13px;
                border-bottom: 3px solid transparent;
            }}
            QPushButton:hover {{
                color: {t.get("text_main")};
                background-color: {t.get("bg_toolbar")};
            }}
            QPushButton:checked {{
                color: {t.get("accent")};
                border-bottom: 3px solid {t.get("accent")};
                background-color: {t.get("bg_main")};
            }}
        """)

    def init_buttons(self):
        # Define Modules: (ID, Key, IconPath)
        modules = [
            (0, "module_audio", "audio_icon.png"),
            (1, "module_video", "video_icon.png"),
            (2, "module_photo", "photo_icon.png")
        ]
        
        for idx, key, icon in modules:
            name = self.localizer.get(key) if self.localizer else key.split("_")[1].upper()
            btn = QPushButton(name)
            btn.setProperty("key", key)
            btn.setCheckable(True)
            btn.setFixedSize(120, 50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            if idx == 0:
                btn.setChecked(True)
                
            self.btn_group.addButton(btn, idx)
            self.layout.addWidget(btn)

    def retranslate_ui(self):
        if not self.localizer: return
        for btn in self.btn_group.buttons():
            key = btn.property("key")
            if key:
                btn.setText(self.localizer.get(key))

    def on_btn_clicked(self, btn_id):
        self.module_changed.emit(btn_id)
