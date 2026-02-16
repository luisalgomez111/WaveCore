from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFrame
from PyQt6.QtCore import Qt, QSize, QUrl, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QColor, QDesktopServices
from PyQt6.QtSvgWidgets import QSvgWidget
import os
import utils.constants as constants

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
                border: none;
                background: transparent;
            }
            QPushButton {
                background-color: #333;
                color: #e0e0e0;
                border: 1px solid #444;
                padding: 8px 25px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #D75239;
                border: 1px solid #D75239;
                color: white;
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
        self.parent_window = parent
        self.localizer = parent.localizer if parent and hasattr(parent, 'localizer') else None
        
        self.setWindowTitle(title)
        self.setFixedWidth(1450)
        self.setMinimumHeight(820)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        # MASTER STYLESHEET: Total Border Cleanliness and Consistent Aesthetics
        self.setStyleSheet("""
            QDialog {
                background-color: #0b0b0b;
                color: #e0e0e0;
                border: 1px solid #1a1a1a;
            }
            QWidget, QLabel, QFrame, QSvgWidget {
                border: none;
                background: transparent;
                outline: none;
            }
            QLabel {
                color: #dddddd;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                border: none;
                background: transparent;
            }
            QPushButton#btn_close {
                background-color: #D75239;
                color: white;
                border: none;
                padding: 20px 80px;
                border-radius: 12px;
                font-weight: 800;
                font-size: 18px;
                letter-spacing: 1px;
            }
            QPushButton#btn_close:hover {
                background-color: #ff6d50;
            }
            QFrame#support_box {
                background-color: #121212;
                border: 1px solid #1a1a1a;
                border-radius: 16px;
            }
            QPushButton.sidebar-btn, QPushButton.donation-btn {
                background-color: #1a1a1a;
                color: #ddd;
                border: 1px solid #222;
                padding: 15px 30px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 700;
                outline: none;
                margin: 4px; /* Increased margin to prevent border clipping */
            }
            QPushButton.sidebar-btn:hover, QPushButton.donation-btn:hover {
                background-color: #222;
                border-color: #D75239;
                color: white;
                outline: none;
            }
        """)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- SIDEBAR: Brand & Logo ---
        sidebar_outer = QFrame()
        sidebar_outer.setFixedWidth(380)
        sidebar_outer.setStyleSheet("background-color: #050505; border-right: 1px solid #121212;")
        sidebar_layout = QVBoxLayout(sidebar_outer)
        sidebar_layout.setContentsMargins(20, 100, 20, 100) # Increased usable space for buttons
        
        lbl_logo = QLabel()
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setStyleSheet("border: none; background: transparent;")
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(current_dir, "resources", "icons", "WaveCore.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            lbl_logo.setPixmap(pixmap.scaled(280, 280, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(lbl_logo)
        
        app_name_lbl = QLabel("WaveCore")
        app_name_lbl.setStyleSheet("font-size: 34px; font-weight: 900; color: white; margin-top: 35px; border: none; background: transparent;")
        app_name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(app_name_lbl)
        
        version_lbl = QLabel(f"v{constants.VERSION} Professional")
        version_lbl.setStyleSheet("color: #D75239; font-size: 14px; font-weight: 800; letter-spacing: 2px; border: none; background: transparent;")
        version_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(version_lbl)
        
        sidebar_layout.addStretch()
        
        # Standardized Buttons (Web & GitHub)
        btn_web = QPushButton(self.tr("btn_visit_web", "VISIT WEBSITE"))
        btn_web.setProperty("class", "sidebar-btn")
        btn_web.setFixedWidth(300) # Increased width
        btn_web.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_web.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://wave-core.vercel.app/")))
        
        web_btn_container = QHBoxLayout()
        web_btn_container.setContentsMargins(5, 5, 5, 5) # Added margins to prevent clipping
        web_btn_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        web_btn_container.addWidget(btn_web)
        sidebar_layout.addLayout(web_btn_container)
        
        sidebar_layout.addSpacing(15)
        
        btn_github = QPushButton("GITHUB REPOSITORY")
        btn_github.setProperty("class", "sidebar-btn")
        btn_github.setFixedWidth(300) # Increased width
        btn_github.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/luisalgomez111/WaveCore")))
        
        github_btn_container = QHBoxLayout()
        github_btn_container.setContentsMargins(5, 5, 5, 5) # Added margins to prevent clipping
        github_btn_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        github_btn_container.addWidget(btn_github)
        sidebar_layout.addLayout(github_btn_container)
        
        main_layout.addWidget(sidebar_outer)
        
        # --- CONTENT AREA ---
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(60, 60, 60, 60)
        content_layout.setSpacing(50)
        
        # Header text
        header_title = QLabel(self.tr("welcome_header", "Elevate Your Creative Workflow"))
        header_title.setStyleSheet("font-size: 44px; font-weight: 900; color: white; border: none; background: transparent;")
        content_layout.addWidget(header_title)
        
        sub_text = QLabel(self.tr("welcome_sub", "The ultimate local vault for professional media assets. Powered by speed, designed for clarity."))
        sub_text.setStyleSheet("font-size: 18px; color: #888; line-height: 1.6; margin-bottom: 5px; border: none; background: transparent;")
        sub_text.setWordWrap(True)
        content_layout.addWidget(sub_text)
        
        # Module Cards (Strict Symmetry)
        showcase_container = QWidget()
        showcase_layout = QHBoxLayout(showcase_container)
        showcase_layout.setContentsMargins(0, 0, 0, 0)
        showcase_layout.setSpacing(40)
        showcase_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        modules = [
            ("AUDIO", "music.svg", self.tr("module_audio_desc", "Waveform scrubbing and precise export.")),
            ("VIDEO", "film.svg", self.tr("module_video_desc", "Smooth playback and cinematic indexing.")),
            ("PHOTO", "image.svg", self.tr("module_photo_desc", "HD metadata vault and gallery view."))
        ]
        
        icon_dir = os.path.join(current_dir, "resources", "icons")
        
        for name, icon_file, desc in modules:
            card = QFrame()
            card.setObjectName("ModuleCard")
            card.setFixedSize(280, 240)
            card.setStyleSheet("""
                QFrame#ModuleCard {
                    background-color: #141414;
                    border: 1px solid #1d1d1d;
                    border-radius: 12px;
                }
                QLabel {
                    border: none;
                    background: transparent;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(20, 30, 20, 30)
            card_layout.setSpacing(15)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            icon_path = os.path.join(icon_dir, icon_file)
            if os.path.exists(icon_path):
                svg_icon = QSvgWidget(icon_path)
                svg_icon.setFixedSize(64, 64)
                svg_icon.setStyleSheet("border: none; background: transparent;")
                card_layout.addWidget(svg_icon, 0, Qt.AlignmentFlag.AlignCenter)
            
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("font-weight: 900; color: white; font-size: 16px; letter-spacing: 1px; border: none; background: transparent;")
            name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(name_lbl)
            
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet("color: #6a6a6a; font-size: 13px; border: none; background: transparent;")
            desc_lbl.setWordWrap(True)
            desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(desc_lbl)
            
            showcase_layout.addWidget(card)
            
        content_layout.addWidget(showcase_container)
        
        # --- Support Section ---
        support_box = QFrame()
        support_box.setObjectName("support_box")
        support_box_layout = QVBoxLayout(support_box)
        support_box_layout.setContentsMargins(30, 20, 30, 20)
        support_box_layout.setSpacing(12)
        
        support_top = QHBoxLayout()
        support_title = QLabel(self.tr("welcome_support_title", "SUPPORT WAVECORE"))
        support_title.setStyleSheet("font-size: 13px; font-weight: 900; color: white; letter-spacing: 2px; border: none; background: transparent;")
        support_top.addWidget(support_title)
        support_top.addStretch()
        support_box_layout.addLayout(support_top)
        
        support_desc = QLabel(self.tr("welcome_support_desc", "Help us maintain servers and develop new features by donating to the project."))
        support_desc.setStyleSheet("color: #777; font-size: 14px; border: none; background: transparent;")
        support_box_layout.addWidget(support_desc)
        
        donate_row = QHBoxLayout()
        donate_row.setSpacing(15)
        
        btn_paypal = QPushButton("PayPal")
        btn_paypal.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_paypal.setProperty("class", "donation-btn")
        btn_paypal.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(constants.PAYPAL_URL)))
        donate_row.addWidget(btn_paypal)
        
        btn_binance = QPushButton("Binance (USDT)")
        btn_binance.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_binance.setProperty("class", "donation-btn")
        btn_binance.clicked.connect(self.copy_binance)
        donate_row.addWidget(btn_binance)
        
        donate_row.addStretch()
        support_box_layout.addLayout(donate_row)
        content_layout.addWidget(support_box)
        
        content_layout.addStretch()
        
        # Bottom Actions
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        
        button_text = self.localizer.get("btn_welcome_start") if self.localizer else "GET STARTED"
        btn_close = QPushButton(button_text)
        btn_close.setObjectName("btn_close")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.accept)
        footer_layout.addWidget(btn_close)
        
        content_layout.addLayout(footer_layout)
        main_layout.addWidget(content_container)

    def tr(self, key, default):
        """Helper to get localized string or default."""
        if self.localizer:
            val = self.localizer.get(key)
            if val and val != key:
                return val
        return default

    def copy_binance(self):
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(constants.BINANCE_ADR)
        sender = self.sender()
        if sender:
            old_text = sender.text()
            success_text = self.tr("welcome_copy_success", "ADDRESS COPIED!")
            sender.setText(success_text)
            sender.setStyleSheet("background-color: #D75239; color: white; border-color: #D75239;")
            QTimer.singleShot(2000, lambda: self.reset_button(sender, old_text))

    def reset_button(self, btn, text):
        btn.setText(text)
        btn.setStyleSheet("")
