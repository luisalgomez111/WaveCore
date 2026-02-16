from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QMessageBox, QLabel)
from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtCore import Qt, QTimer, QSettings

# Utils & Core
from utils.localization import Localizer
from audio.player import AudioPlayer
from utils.favorites_manager import FavoritesManager
from utils.themes import ThemeManager
import utils.file_ops as fops
import os

# UI Components
from ui.navigation.BottomBar import BottomBar
from ui.modules.AudioPage import AudioPage
from ui.modules.VideoPage import VideoPage
from ui.modules.PhotoPage import PhotoPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Settings
        self.settings = QSettings("DR_Audio", "DR_Player")
        
        # Shared Resources
        self.player = AudioPlayer()
        self.localizer = Localizer("es")
        self.fav_manager = FavoritesManager()
        
        # Theme Management (Locked to Dark)
        self.theme_manager = ThemeManager("dark")
        
        # --- INIT UI ---
        self.init_ui()
        self.apply_theme()
        self.update_ui_text()
        
        # Deferred Welcome Screen
        QTimer.singleShot(1000, self.show_welcome_screen)

    def init_ui(self):
        self.resize(1200, 800)
        self.create_menu_bar()
        
        # Central Widget
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #121212;")
        self.setCentralWidget(central_widget)
        
        # Main Layout
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # --- STACKED WIDGET (PAGES) ---
        self.pages_stack = QStackedWidget()
        
        # Initialize Pages
        # Pass self to allow pages to access shared resources (player, settings, etc)
        self.audio_page = AudioPage(self)
        self.video_page = VideoPage(self)
        self.photo_page = PhotoPage(self)
        
        self.pages_stack.addWidget(self.audio_page) # Index 0
        self.pages_stack.addWidget(self.video_page) # Index 1
        self.pages_stack.addWidget(self.photo_page) # Index 2
        
        self.main_layout.addWidget(self.pages_stack)
        
        # --- BOTTOM BAR ---
        self.bottom_bar = BottomBar(self.localizer)
        self.bottom_bar.module_changed.connect(self.switch_module)
        self.main_layout.addWidget(self.bottom_bar)

    def apply_theme(self):
        t = self.theme_manager
        
        # Main Window & Menu
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {t.get("bg_main")}; color: {t.get("text_main")}; font-family: 'Segoe UI', sans-serif; }}
            QMenuBar {{ background-color: {t.get("bg_secondary")}; color: {t.get("text_main")}; border-bottom: 1px solid {t.get("border")}; padding: 2px; }}
            QMenuBar::item {{ spacing: 3px; padding: 4px 10px; background: transparent; }}
            QMenuBar::item:selected {{ background-color: {t.get("bg_button")}; }}
            QMenu {{ background-color: {t.get("bg_secondary")}; color: {t.get("text_main")}; border: 1px solid {t.get("border")}; }}
            QMenu::item:selected {{ background-color: {t.get("accent")}; color: white; }}
        """)
        
        # Propagate to children
        if hasattr(self, 'bottom_bar'): self.bottom_bar.apply_theme(t)
        if hasattr(self, 'audio_page'): self.audio_page.apply_theme(t)
        if hasattr(self, 'video_page'): self.video_page.apply_theme(t)
        if hasattr(self, 'photo_page'): self.photo_page.apply_theme(t)

    def switch_module(self, index):
        self.pages_stack.setCurrentIndex(index)

    def show_welcome_screen(self):
        from ui.dialogs import WelcomeDialog
        title = self.localizer.get("dialog_welcome_title")
        html = self.localizer.get("dialog_welcome_html")
        dlg = WelcomeDialog(title, html, self)
        dlg.exec()

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.clear()
        
        # Logo
        logo_label = QLabel()
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(current_dir, "resources", "icons", "WaveCore.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaledToHeight(22, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setContentsMargins(10, 0, 5, 0)
            menu_bar.setCornerWidget(logo_label, Qt.Corner.TopLeftCorner)
        
        # File Menu
        self.file_menu = menu_bar.addMenu("")
        
        self.import_action = QAction("", self)
        self.import_action.setShortcut("Ctrl+I")
        self.import_action.triggered.connect(self.on_import_action)
        self.file_menu.addAction(self.import_action)
        
        self.exit_action = QAction("", self)
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)


        # Help Menu
        self.help_menu = menu_bar.addMenu("")
        
        self.creator_action = QAction("", self)
        self.creator_action.triggered.connect(self.show_creator_dialog)
        self.help_menu.addAction(self.creator_action)

        self.about_action = QAction("", self)
        self.about_action.triggered.connect(self.show_about_dialog)
        self.help_menu.addAction(self.about_action)
        
        self.help_menu.addSeparator()
        self.update_action = QAction("Buscar Actualizaciones", self)
        self.update_action.triggered.connect(self.check_for_updates_ui)
        self.help_menu.addAction(self.update_action)


    def update_ui_text(self):
        self.setWindowTitle("WaveCore v2.0")
        self.file_menu.setTitle(self.localizer.get("menu_file"))
        self.import_action.setText(self.localizer.get("menu_import"))
        self.exit_action.setText(self.localizer.get("menu_exit"))
        self.help_menu.setTitle(self.localizer.get("menu_help"))
        self.creator_action.setText(self.localizer.get("menu_creator"))
        self.about_action.setText(self.localizer.get("menu_about"))
        self.update_action.setText(self.localizer.get("menu_updates"))

    def on_import_action(self):
        # Delegate to current page if supported
        current_widget = self.pages_stack.currentWidget()
        if current_widget == self.audio_page:
            # We can expose a method in AudioPage
            # For now, replicate dialog here or call AudioPage method?
            # Better to let AudioPage handle it.
            # But AudioPage logic is: "import" -> add_folder_to_library
            folder = QFileDialog.getExistingDirectory(self, self.localizer.get("dialog_select_folder"))
            if folder:
                self.audio_page.add_folder_to_library(folder)
        else:
            QMessageBox.information(self, "Import", "Import not supported for this module yet.")

    def show_about_dialog(self):
        from ui.dialogs import CustomDialog
        html = self.localizer.get("dialog_about_html")
        dlg = CustomDialog(self.localizer.get("dialog_about_title"), html, self, width=850)
        dlg.exec()

    def show_creator_dialog(self):
        from ui.dialogs import CustomDialog
        info = self.localizer.get("dialog_creator_info").replace("\n", "<br>")
        title_text = self.localizer.get("dialog_creator_text")
        html = f"<h2 style='color: #D75239;'>{title_text}</h2><p>{info}</p>"
        dlg = CustomDialog(self.localizer.get("dialog_creator_title"), html, self, width=750)
        dlg.exec()

    def check_for_updates_ui(self):
        from utils.updater import check_for_updates
        import webbrowser
        
        update_available, latest_version, download_url = check_for_updates()
        
        if update_available:
            title = self.localizer.get("status_update_available")
            msg = self.localizer.get("status_update_msg").format(latest_version)
            
            reply = QMessageBox.question(self, title, msg,
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes and download_url:
                webbrowser.open(download_url)
        else:
            QMessageBox.information(self, self.localizer.get("window_title"), 
                                    self.localizer.get("status_no_updates"))
            
    def closeEvent(self, event):
        # Save Audio Page State
        if hasattr(self, 'audio_page'):
            self.audio_page.save_state()
        super().closeEvent(event)
