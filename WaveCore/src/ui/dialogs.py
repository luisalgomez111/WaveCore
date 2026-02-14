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
class WelcomeDialog(QDialog):
    def __init__(self, title, content_html, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedWidth(650)
        self.setMinimumHeight(400)
        
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
                line-height: 1.5;
            }
            QPushButton {
                background-color: #D75239;
                color: white;
                border: none;
                padding: 8px 25px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ff6d50;
            }
        """)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar with Logo
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #121212; border-right: 1px solid #2a2a2a;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_logo = QLabel()
        import os
        from PyQt6.QtGui import QPixmap
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(current_dir, "resources", "icons", "WaveCore.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Large logo
            scaled_pixmap = pixmap.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_logo.setPixmap(scaled_pixmap)
        
        sidebar_layout.addWidget(lbl_logo)
        sidebar_layout.addSpacing(20)
        
        lbl_brand = QLabel("WAVECORE")
        lbl_brand.setStyleSheet("font-weight: bold; font-size: 18px; color: #D75239; letter-spacing: 2px;")
        sidebar_layout.addWidget(lbl_brand)
        
        main_layout.addWidget(sidebar)
        
        # Right Side Content
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(15)
        
        lbl_content = QLabel(content_html)
        lbl_content.setWordWrap(True)
        lbl_content.setOpenExternalLinks(True)
        lbl_content.setTextFormat(Qt.TextFormat.RichText)
        content_layout.addWidget(lbl_content)
        
        content_layout.addStretch()
        
        btn_close = QPushButton("COMENZAR")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        content_layout.addLayout(btn_layout)
        
        main_layout.addWidget(content_container)
