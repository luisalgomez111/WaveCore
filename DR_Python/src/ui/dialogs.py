from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class CustomDialog(QDialog):
    def __init__(self, title, content_html, parent=None, width=500):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(width)
        
        # Remove context help button (?)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #333;
            }
            QLabel {
                color: #cccccc;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                line-height: 1.4;
            }
            QPushButton {
                background-color: #333;
                color: white;
                border: 1px solid #444;
                padding: 6px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D75239; /* Brand color */
                border: 1px solid #D75239;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Content
        lbl_content = QLabel(content_html)
        lbl_content.setWordWrap(True)
        lbl_content.setOpenExternalLinks(True)
        lbl_content.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(lbl_content)
        
        # Close Button
        btn_close = QPushButton("OK")
        btn_close.clicked.connect(self.accept)
        btn_close.setFixedWidth(100)
        
        # Center button
        btn_container = QWidget()
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(0,0,0,0)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(btn_close)
        
        layout.addWidget(btn_container)
