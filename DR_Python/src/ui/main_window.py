from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QListWidget, QFileDialog, QListWidgetItem, 
                             QSplitter, QTreeWidget, QTreeWidgetItem, QMessageBox, QLabel, QMenu, QButtonGroup,
                             QTabWidget, QLineEdit, QStackedWidget, QTableView, QHeaderView, QInputDialog)
from PyQt6.QtGui import QAction, QIcon, QCursor, QColor, QBrush, QPixmap
from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import Qt, QSize, QDir, QTimer, QSettings, QUrl, pyqtSignal, QPoint
from utils.localization import Localizer
from ui.playback_bar import PlaybackBar
from audio.player import AudioPlayer
import utils.file_ops as fops
from ui.library_model import LibraryModel
from ui.track_delegate import TrackDelegate
from utils.scanner_thread import ScannerThread
from utils.favorites_manager import FavoritesManager
from utils.library_cache import get_cached_folder_data, save_folder_to_cache
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Settings
        self.settings = QSettings("DR_Audio", "DR_Player")
        
        # Audio Player
        self.player = AudioPlayer()
        self.player.position_changed.connect(self.on_player_position_changed)
        self.player.state_changed.connect(self.on_player_state_changed)
        
        # Default Language
        self.localizer = Localizer("es")
        
        # Favorites Manager
        self.fav_manager = FavoritesManager()
        
        # --- UI ELEMENTS ---
        
        # --- INIT UI ---
        self.init_ui()
        self.update_ui_text()
        
        # --- LOAD VAULT ---
        self.load_vault()

    def load_vault(self):
        vault_path = fops.ensure_vault_exists()
        if vault_path:
            # Initial Load
            self.add_folder_to_library(vault_path)
            
            # Watch for external changes
            from PyQt6.QtCore import QFileSystemWatcher
            self.watcher = QFileSystemWatcher(self)
            self.watcher.addPath(vault_path)
            self.watcher.directoryChanged.connect(self.on_vault_changed)
            
    def on_vault_changed(self, path):
        # Reload library tree to show new files/folders
        # We need to be careful not to lose expansion state or selection if possible,
        # but for now a simple reload is robust.
        self.library_tree.clear()
        self.add_folder_to_library(path)
            
    def init_ui(self):
        self.resize(1200, 800)
        self.create_menu_bar()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Vertical Layout: [Splitter (Content)] / [PlaybackBar]
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- SPLITTER (Sidebar + List) ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sidebar
        # Sidebar
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # --- TABS: Library / Online ---
        # TABS: Library / Online
        self.sidebar_tabs = QTabWidget()
        self.sidebar_tabs.tabBar().setDocumentMode(True)
        self.sidebar_tabs.tabBar().setExpanding(True)
        
        self.sidebar_tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background: #1f1f1f;
                color: #888;
                padding: 8px 15px;
                border-bottom: 2px solid #333;
                min-width: 80px; /* Ensure they don't shrink too small */
            }
            QTabBar::tab:selected {
                color: #D75239;
                border-bottom: 2px solid #D75239;
                font-weight: bold;
            }
        """)
        
        # TAB 1: LIBRARY
        tab_library = QWidget()
        lib_layout = QVBoxLayout(tab_library)
        lib_layout.setContentsMargins(0, 0, 0, 0)
        lib_layout.setSpacing(0)
        
        # Add Category Button
        self.btn_add_category = QPushButton(self.localizer.get("ctx_new_folder"))
        self.btn_add_category.setStyleSheet("""
            QPushButton {
                background-color: #333; 
                color: #ddd; 
                border: none; 
                padding: 5px; 
                border-radius: 3px;
                text-align: left;
                padding-left: 10px;
                margin: 5px;
            }
            QPushButton:hover { background-color: #444; }
        """)
        self.btn_add_category.clicked.connect(lambda: self.action_create_folder(None))
        lib_layout.addWidget(self.btn_add_category)

        self.library_tree = QTreeWidget()
        self.library_tree.setHeaderHidden(True)
        self.library_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1a1a1a;
                border: none;
                color: #ccc;
                outline: none;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #D75239;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #333;
            }
        """)
        self.library_tree.itemClicked.connect(self.on_category_selected)
        self.library_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.library_tree.customContextMenuRequested.connect(self.open_sidebar_menu)
        
        # Add Special Favorites Category
        self.fav_item = QTreeWidgetItem(self.library_tree)
        self.fav_item.setText(0, "★ Favorites")
        self.fav_item.setData(0, Qt.ItemDataRole.UserRole, "favorites_internal")
        from PyQt6.QtGui import QColor
        self.fav_item.setForeground(0, QColor("#FFB347")) # Elegant Amber/Gold
        
        lib_layout.addWidget(self.library_tree)
        
        self.sidebar_tabs.addTab(tab_library, "Library")
        
        # TAB 2: ONLINE (Freesound)
        # Now acts as a button to switch view
        tab_online = QWidget()
        online_tab_layout = QVBoxLayout(tab_online)
        # Intro label or history?
        lbl_intro = QLabel("Search Freesound\nin the main view ->")
        lbl_intro.setStyleSheet("color: #666; font-style: italic; margin-top: 20px;")
        lbl_intro.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        online_tab_layout.addWidget(lbl_intro)
        online_tab_layout.addStretch()
        
        self.sidebar_tabs.addTab(tab_online, "Online")
        
        # Connect Tab Switch to Main View Switch
        self.sidebar_tabs.currentChanged.connect(self.on_tab_changed)
        
        sidebar_layout.addWidget(self.sidebar_tabs)
        
        splitter.addWidget(sidebar_widget)
        
        # Track List Layout (Right Side)
        self.right_stack = QStackedWidget()
        
        # --- PAGE 1: LOCAL LIBRARY ---
        local_widget = QWidget()
        local_layout = QVBoxLayout(local_widget)
        local_layout.setContentsMargins(0, 0, 0, 0)
        local_layout.setSpacing(0)
        
        from constants import LibraryColumns
        
        # Local Header matching new columns
        local_header = QWidget()
        local_header.setFixedHeight(30)
        local_header.setStyleSheet("background-color: #1a1a1a; border-bottom: 1px solid #333;")
        lh_layout = QHBoxLayout(local_header)
        lh_layout.setContentsMargins(0, 0, 0, 0) # No side margins
        lh_layout.setSpacing(0)
        
        def add_h_lbl(layout, text, width=None, align=Qt.AlignmentFlag.AlignLeft, expand=False):
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #888; font-size: 11px; font-weight: bold; text-transform: uppercase;")
            lbl.setContentsMargins(5, 0, 5, 0) # Match Delegate padding
            
            if width:
                if expand:
                    lbl.setMinimumWidth(width)
                else:
                    lbl.setFixedWidth(width)
            
            lbl.setAlignment(align | Qt.AlignmentFlag.AlignVCenter)
            if expand: 
                layout.addWidget(lbl, 1)
            else:
                layout.addWidget(lbl)

        # Build Header from Constants
        for i, key in enumerate(LibraryColumns.HEADERS_KEYS):
            header_text = self.localizer.get(key)
            width = LibraryColumns.WIDTHS[i]
            align = Qt.AlignmentFlag.AlignLeft
            expand = False # Disabling expansion to cluster columns to the left
            
            if i == LibraryColumns.INDEX: align = Qt.AlignmentFlag.AlignRight
            elif i in (LibraryColumns.FAV, LibraryColumns.CHANNELS, LibraryColumns.FORMAT, LibraryColumns.DURATION): 
                align = Qt.AlignmentFlag.AlignCenter
            
            # Special case for Star col width if needed
            add_h_lbl(lh_layout, header_text, width, align, expand)

        # Scrollbar Spacer - Push everything else to the left
        lh_layout.addStretch() # This pushes all columns to the left
        header_spacer = QWidget()
        header_spacer.setFixedWidth(15) 
        lh_layout.addWidget(header_spacer)

        local_layout.addWidget(local_header)
        
        # --- TABLE VIEW ---
        self.library_model = LibraryModel(self)
        self.track_delegate = TrackDelegate(self)
        
        self.track_view = QTableView()
        self.track_view.setModel(self.library_model)
        self.track_view.setItemDelegate(self.track_delegate)
        
        self.track_view.setShowGrid(False)
        self.track_view.verticalHeader().setVisible(False)
        self.track_view.horizontalHeader().setVisible(False) # Using custom header widget
        
        self.track_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.track_view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.track_view.setAlternatingRowColors(False)
        self.track_view.setStyleSheet("background-color: #121212; border: none;")
        self.track_view.setVerticalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.track_view.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        
        # Drag disabled
        self.track_view.setDragEnabled(False)
        
        header = self.track_view.horizontalHeader()
        for i in range(LibraryColumns.COUNT):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
            header.resizeSection(i, LibraryColumns.WIDTHS[i])
        # Context Menu & Click Events
        self.track_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.track_view.customContextMenuRequested.connect(self.open_track_menu)
        self.track_view.clicked.connect(self.on_track_clicked)
        self.track_view.doubleClicked.connect(self.on_track_double_clicked)
        
        local_layout.addWidget(self.track_view)
        
        self.right_stack.addWidget(local_widget)
        
        # --- PAGE 2: ONLINE RESULTS ---
        online_widget = QWidget()
        online_layout = QVBoxLayout(online_widget)
        online_layout.setContentsMargins(0, 0, 0, 0)
        online_layout.setSpacing(0)
        
        # Search Bar Area
        search_area = QWidget()
        search_area.setStyleSheet("background-color: #1f1f1f; border-bottom: 1px solid #333;")
        search_area_layout = QHBoxLayout(search_area)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Freesound...")
        self.search_input.setStyleSheet("background-color: #333; color: white; border: 1px solid #444; padding: 5px; border-radius: 3px;")
        self.search_input.returnPressed.connect(self.search_freesound)
        
        btn_search = QPushButton("SEARCH")
        btn_search.setStyleSheet("QPushButton { background-color: #D75239; color: white; border: none; padding: 6px 15px; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #ff6d50; }")
        btn_search.clicked.connect(self.search_freesound)
        
        search_area_layout.addWidget(self.search_input)
        search_area_layout.addWidget(btn_search)
        online_layout.addWidget(search_area)
        
        # Online Header
        online_header = QWidget()
        online_header.setFixedHeight(30)
        online_header.setStyleSheet("background-color: #1a1a1a; border-bottom: 1px solid #333;")
        oh_layout = QHBoxLayout(online_header)
        oh_layout.setContentsMargins(0, 0, 0, 0)
        oh_layout.setSpacing(0)
        
        add_h_lbl(oh_layout, "#", 40, Qt.AlignmentFlag.AlignRight)
        add_h_lbl(oh_layout, "", 25) # Play space
        add_h_lbl(oh_layout, "Name", 200)
        add_h_lbl(oh_layout, "Format", 60, Qt.AlignmentFlag.AlignCenter)
        add_h_lbl(oh_layout, "Duration", 70, Qt.AlignmentFlag.AlignRight)
        add_h_lbl(oh_layout, "Description", 150)
        add_h_lbl(oh_layout, "Action", expand=True) 

        # Scrollbar Spacer
        oh_spacer = QWidget()
        oh_spacer.setFixedWidth(15)
        oh_layout.addWidget(oh_spacer)
        
        online_layout.addWidget(online_header)
        
        self.online_list = QListWidget()
        self.online_list.setStyleSheet("background-color: #121212; border: none;")
        self.online_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        online_layout.addWidget(self.online_list)
        
        self.right_stack.addWidget(online_widget)
        
        splitter.addWidget(self.right_stack)
        splitter.setSizes([250, 950])
        
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.setHandleWidth(1)
        self.main_splitter.setStyleSheet("QSplitter::handle { background-color: #2a2a2a; }")
        
        self.main_splitter.addWidget(splitter)
        
        # --- PLAYBACK BAR ---
        self.playback_bar = PlaybackBar()
        self.playback_bar.play_clicked.connect(self.player.play)
        self.playback_bar.pause_clicked.connect(self.player.pause)
        self.playback_bar.speed_changed.connect(self.player.set_playback_rate)
        self.playback_bar.seek_requested.connect(self.on_seek_requested)
        self.playback_bar.volume_changed.connect(self.player.set_volume)
        
        self.main_splitter.addWidget(self.playback_bar)
        self.main_splitter.setCollapsible(1, False)
        self.main_splitter.setSizes([850, 150])
        
        main_layout.addWidget(self.main_splitter)
        self.restore_splitter_state()

        # Shortcuts
        from PyQt6.QtGui import QShortcut, QKeySequence
        self.space_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        self.space_shortcut.activated.connect(self.player.toggle_play)

        # Styles
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
            QMenuBar { background-color: #1a1a1a; color: #cccccc; border-bottom: 1px solid #2a2a2a; padding: 2px; }
            QMenuBar::item { spacing: 3px; padding: 4px 10px; background: transparent; }
            QMenuBar::item:selected { background-color: #333333; }
        """)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.clear()
        
        # Add Logo to the left corner of the menu bar
        logo_label = QLabel()
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(current_dir, "resources", "icons", "WaveCore.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale logo to reasonable menu bar height (e.g., 22px) keeping aspect ratio
            scaled_pixmap = pixmap.scaledToHeight(22, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setContentsMargins(10, 0, 5, 0)
            menu_bar.setCornerWidget(logo_label, Qt.Corner.TopLeftCorner)
        
        self.file_menu = menu_bar.addMenu("")
        
        self.import_action = QAction("", self)
        self.import_action.setShortcut("Ctrl+I")
        self.import_action.triggered.connect(self.import_folder_dialog)
        self.file_menu.addAction(self.import_action)
        
        self.exit_action = QAction("", self)
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)
        
        self.lang_menu = menu_bar.addMenu("")
        
        langs = [("English", "en"), ("Español", "es"), ("Русский", "ru"), ("中文", "zh"), ("Français", "fr")]
        for name, code in langs:
             action = QAction(name, self)
             action.triggered.connect(lambda checked, c=code: self.change_language(c))
             self.lang_menu.addAction(action)

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

    def change_language(self, lang_code):
        self.localizer.set_language(lang_code)
        self.update_ui_text()

    def update_ui_text(self):
        self.setWindowTitle(self.localizer.get("window_title"))
        self.file_menu.setTitle(self.localizer.get("menu_file"))
        self.import_action.setText(self.localizer.get("menu_import"))
        self.exit_action.setText(self.localizer.get("menu_exit"))
        self.lang_menu.setTitle(self.localizer.get("menu_language"))
        self.help_menu.setTitle(self.localizer.get("menu_help"))
        self.creator_action.setText(self.localizer.get("menu_creator"))
        self.about_action.setText(self.localizer.get("menu_about"))
        self.update_action.setText(self.localizer.get("menu_updates"))

    def show_about_dialog(self):
        from ui.dialogs import CustomDialog
        html = self.localizer.get("dialog_about_html")
        dlg = CustomDialog(self.localizer.get("dialog_about_title"), html, self, width=600)
        dlg.exec()

    def show_creator_dialog(self):
        from ui.dialogs import CustomDialog
        info = self.localizer.get("dialog_creator_info").replace("\n", "<br>")
        title_text = self.localizer.get("dialog_creator_text")
        html = f"<h2 style='color: #D75239;'>{title_text}</h2><p>{info}</p>"
        dlg = CustomDialog(self.localizer.get("dialog_creator_title"), html, self, width=500)
        dlg.exec()

    def import_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, self.localizer.get("dialog_select_folder"))
        if folder:
            self.add_folder_to_library(folder)

    def check_for_updates_ui(self):
        from utils.updater import check_for_updates
        from PyQt6.QtWidgets import QMessageBox
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

    def add_folder_to_library(self, folder_path):
        folder_name = os.path.basename(folder_path)
        root_item = QTreeWidgetItem(self.library_tree)
        root_item.setText(0, folder_name)
        root_item.setData(0, Qt.ItemDataRole.UserRole, folder_path)
        root_item.setExpanded(True)
        try:
            entries = sorted(os.listdir(folder_path))
            for entry in entries:
                full_path = os.path.join(folder_path, entry)
                if os.path.isdir(full_path):
                    cat_item = QTreeWidgetItem(root_item)
                    cat_item.setText(0, entry)
                    cat_item.setData(0, Qt.ItemDataRole.UserRole, full_path)
        except Exception as e:
            print(f"Error reading folder: {e}")
            
    def on_category_selected(self, item, column):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path == "favorites_internal":
            self.load_favorites_list()
        elif path and os.path.isdir(path):
            self.scan_and_display_files(path)

    def load_favorites_list(self):
        if hasattr(self, 'scanner_thread') and self.scanner_thread.isRunning():
            self.scanner_thread.stop()
            
        self.library_model.clear()
        paths = self.fav_manager.get_all()
        if not paths: return
        
        self.scanner_thread = ScannerThread(file_paths=paths)
        self.scanner_thread.batch_found.connect(self.on_scan_batch)
        self.scanner_thread.finished_scan.connect(self.on_scan_finished)
        self.scanner_thread.start()


    def scan_and_display_files(self, folder_path):
        
        # Stop existing scan if any
        if hasattr(self, 'scanner_thread') and self.scanner_thread.isRunning():
            self.scanner_thread.stop()
            
        self.library_model.clear()
        
        # 1. Check Cache
        cached_tracks = get_cached_folder_data(folder_path)
        if cached_tracks:
            print(f"Loading {folder_path} from cache...")
            import numpy as np
            # Convert lists back to numpy for consistent usage
            for t in cached_tracks:
                t["waveform"] = np.array(t["waveform"], dtype=np.float32)
                t["is_favorite"] = self.fav_manager.is_favorite(t["path"])
            self.library_model.add_tracks(cached_tracks)
            return

        # 2. No cache, start scan
        print(self.localizer.get("status_loading").format(folder_path))
        self.current_scan_path = folder_path
        self.current_scan_results = []
        
        self.scanner_thread = ScannerThread(folder_path)
        self.scanner_thread.batch_found.connect(self.on_scan_batch_with_cache)
        self.scanner_thread.finished_scan.connect(self.on_scan_finished_with_cache)
        self.scanner_thread.start()

    def on_scan_batch_with_cache(self, tracks):
        # Mark favorites and collect for cache
        for track in tracks:
            track["is_favorite"] = self.fav_manager.is_favorite(track["path"])
            self.current_scan_results.append(track)
        self.library_model.add_tracks(tracks)

    def on_scan_finished_with_cache(self, count):
        from utils.library_cache import save_folder_to_cache
        if hasattr(self, 'current_scan_path') and self.current_scan_results:
            save_folder_to_cache(self.current_scan_path, self.current_scan_results)
        self.on_scan_finished(count)
        
    def on_scan_batch(self, tracks):
        # Mark favorites
        for track in tracks:
            track["is_favorite"] = self.fav_manager.is_favorite(track["path"])
        self.library_model.add_tracks(tracks)
        
    def on_scan_finished(self, count):
        print(self.localizer.get("status_loaded").format(count))
        
    def on_track_clicked(self, index):
        try:
            track = self.library_model.get_track_at(index.row())
            if not track: return

            # Handle Favorite Click
            if index.column() == self.library_model.COL_FAV:
                path = track.get("path")
                is_fav = self.fav_manager.toggle(path)
                track["is_favorite"] = is_fav
                self.library_model.dataChanged.emit(index, index)
                return

            # Handle Play: Now all columns between Play and Duration trigger play
            play_cols = (self.library_model.COL_PLAY, self.library_model.COL_TITLE, 
                         self.library_model.COL_CHANNELS, self.library_model.COL_FORMAT, 
                         self.library_model.COL_DURATION)
            
            if index.column() in play_cols:
                self.play_track(track["path"], track["title"], track["waveform"], track["duration"])
                    
            elif index.column() == self.library_model.COL_WAVEFORM:
                view_pos = self.track_view.viewport().mapFromGlobal(QCursor.pos())
                cell_rect = self.track_view.visualRect(index)
                rel_x = view_pos.x() - cell_rect.x()
                width = cell_rect.width()
                if width > 0:
                    perc = rel_x / width
                    self.on_seek_requested(perc)
                    # Also ensure we are playing THIS track
                    track = self.library_model.get_track_at(index.row())
                    if track:
                        self.play_track(track["path"], track["title"], track["waveform"], track["duration"])
        except Exception as e:
            print(f"Error in on_track_clicked: {e}")
            import traceback
            traceback.print_exc()

    # Double Click handles Play
    def on_track_double_clicked(self, index):
        track = self.library_model.get_track_at(index.row())
        if track:
            self.play_track(track["path"], track["title"], track["waveform"], track["duration"])

    def play_track(self, path, title, data, duration=0):
        try:
            self.current_playing_path = path
            print(f"Playing: {path}")
            self.player.load(path)
            self.player.play()
            self.playback_bar.set_track_info(title, data, path, duration)
            self.playback_bar.set_playing_state(True)
        except Exception as e:
            print(f"CRITICAL ERROR playing track: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Playback Error", f"Could not play track:\n{e}")

    def on_player_position_changed(self, pos_ms):
        duration = self.player.get_duration()
        self.playback_bar.update_progress(pos_ms, duration)
        
    def on_player_state_changed(self, state):
        from PyQt6.QtMultimedia import QMediaPlayer
        is_playing = (state == QMediaPlayer.PlaybackState.PlayingState)
        self.playback_bar.set_playing_state(is_playing)

    def on_seek_requested(self, relative_pos):
        duration = self.player.get_duration()
        if duration > 0:
            seek_ms = int(duration * relative_pos)
            self.player.set_position(seek_ms)

    def restore_splitter_state(self):
        saved_state = self.settings.value("splitter_sizes")
        if saved_state:
            try:
                # Handle cases where value might be stored as string list
                sizes = [int(s) for s in saved_state]
                self.main_splitter.setSizes(sizes)
            except:
                pass 

    def closeEvent(self, event):
        # Save Splitter State
        sizes = self.main_splitter.sizes()
        self.settings.setValue("splitter_sizes", [str(s) for s in sizes])
        super().closeEvent(event)

    # --- CONTEXT MENUS & FILE OPS ---
    def open_sidebar_menu(self, position):
        item = self.library_tree.itemAt(position)
        menu = QMenu()
        
        action_new = menu.addAction(self.localizer.get("ctx_new_folder"))
        action_new.triggered.connect(lambda: self.action_create_folder(item))
        
        if item:
            menu.addSeparator()
            action_rename = menu.addAction(self.localizer.get("ctx_rename"))
            action_rename.triggered.connect(lambda: self.action_rename_folder(item))
            
            action_delete = menu.addAction(self.localizer.get("ctx_delete"))
            action_delete.triggered.connect(lambda: self.action_delete_folder(item))
            
        menu.exec(self.library_tree.viewport().mapToGlobal(position))

    def action_create_folder(self, parent_item):
        # Determine target item
        target_item = parent_item
        if not target_item:
            target_item = self.library_tree.currentItem()
        
        if not target_item:
            if self.library_tree.topLevelItemCount() > 0:
                target_item = self.library_tree.topLevelItem(0) # Default to first root
        
        if not target_item:
            QMessageBox.warning(self, self.localizer.get("window_title"), "Please import a library folder first.")
            return

        target_path = target_item.data(0, Qt.ItemDataRole.UserRole)
        
        # Verify it's a directory
        import os
        if not os.path.isdir(target_path):
             QMessageBox.warning(self, "Error", "Selected item is not a valid folder.")
             return 
            
        text, ok = QInputDialog.getText(self, self.localizer.get("ctx_new_folder"), "Folder Name:")
        if ok and text:
            try:
                new_path = fops.create_new_folder(target_path, text)
                # Refresh UI
                if target_item:
                    # Quick add logic or full refresh
                    import os
                    name = os.path.basename(new_path)
                    new_item = QTreeWidgetItem(target_item)
                    new_item.setText(0, name)
                    new_item.setData(0, Qt.ItemDataRole.UserRole, new_path)
                    target_item.setExpanded(True)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def action_rename_folder(self, item):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        old_name = item.text(0)
        text, ok = QInputDialog.getText(self, "Rename", "New Name:", text=old_name)
        if ok and text and text != old_name:
            try:
                new_path = fops.rename_item(path, text)
                item.setText(0, text)
                item.setData(0, Qt.ItemDataRole.UserRole, new_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def action_delete_folder(self, item):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, "Delete Folder", 
                                     f"Are you sure you want to delete '{item.text(0)}' and all its contents?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                fops.delete_item(path)
                # Remove from tree
                parent = item.parent()
                if parent:
                    parent.removeChild(item)
                else:
                    index = self.library_tree.indexOfTopLevelItem(item)
                    self.library_tree.takeTopLevelItem(index)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def open_track_menu(self, position):
        index = self.track_view.indexAt(position)
        if not index.isValid(): return
        
        track = self.library_model.get_track_at(index.row())
        if not track: return

        menu = QMenu()
        action_rename = menu.addAction(self.localizer.get("ctx_rename_file"))
        action_rename.triggered.connect(lambda: self.action_rename_file(index, track))
        
        action_delete = menu.addAction(self.localizer.get("ctx_delete_file"))
        action_delete.triggered.connect(lambda: self.action_delete_file(index, track))
        
        menu.exec(self.track_view.viewport().mapToGlobal(position))

    def action_rename_file(self, index, track):
        path = track["path"]
        old_name = track["title"]
        
        text, ok = QInputDialog.getText(self, "Rename File", "New Name:", text=old_name)
        if ok and text and text != old_name:
            try:
                new_path = fops.rename_item(path, text)
                # Update model
                self.library_model.update_track_info(index.row(), {"path": new_path, "title": text})
            except Exception as e:
                 QMessageBox.critical(self, "Error", str(e))

    def action_delete_file(self, index, track):
        path = track["path"]
        
        reply = QMessageBox.question(self, "Delete File", 
                                     f"Are you sure you want to delete '{track['title']}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                fops.delete_item(path)
                self.library_model.removeRow(index.row())
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.player.toggle_play()
        else:
            super().keyPressEvent(event)

    # --- INTERNAL DRAG & DROP LOGIC ---
    def tree_drag_enter(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def tree_drag_move(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()
        else:
            event.ignore()

    def tree_drop(self, event):
        # 1. Get Target Folder
        item = self.library_tree.itemAt(event.position().toPoint())
        if not item: return
        
        target_path = item.data(0, Qt.ItemDataRole.UserRole)
        if not target_path or not os.path.isdir(target_path): return
        
        # 2. Get Files
        if not event.mimeData().hasUrls(): return
        
        file_urls = event.mimeData().urls()
        
        import shutil
        moved_count = 0
        
        try:
            for url in file_urls:
                src_path = url.toLocalFile()
                if not os.path.isfile(src_path): continue
                
                filename = os.path.basename(src_path)
                dst_path = os.path.join(target_path, filename)
                
                if src_path == dst_path: continue
                
                print(f"Moving {src_path} -> {dst_path}")
                shutil.move(src_path, dst_path)
                moved_count += 1
            
            if moved_count > 0:
                print(f"Moved {moved_count} files.")
                # Refresh current view if it was the source
                # (Or just let user click again? Auto refresh is nicer)
                # Check if we are viewing the source folder?
                # For now, just refresh the TARGET folder if it's open, 
                # or refresh the list if we were dragging FROM the list.
                # Simplest: self.scan_and_display_files(current_view_path)
                
                current = self.library_tree.currentItem()
                if current:
                    current_path = current.data(0, Qt.ItemDataRole.UserRole)
                    self.scan_and_display_files(current_path)
                
        except Exception as e:
            QMessageBox.critical(self, "Move Error", f"Could not move files: {e}")

    # --- FREESOUND INTEGRATION ---
    def on_tab_changed(self, index):
        # 0 = Library, 1 = Online
        self.right_stack.setCurrentIndex(index)
        if index == 1:
            self.search_input.setFocus()

    def search_freesound(self):
        from utils.freesound_client import FreesoundClient
        from ui.online_track_row import OnlineTrackRow
        
        query = self.search_input.text()
        if not query: return
        
        self.online_list.clear()
        
        # --- AUTO TRANSLATION ---
        try:
            from deep_translator import GoogleTranslator
            # Translates any language to English
            translated = GoogleTranslator(source='auto', target='en').translate(query)
            if translated and translated.lower() != query.lower():
                print(f"Translating '{query}' -> '{translated}'")
                # Update UI to show what we are searching for
                self.search_input.setText(translated) 
                query = translated 
        except Exception as e:
            print(f"Translation failed: {e}")

        # Show loading...
        # TODO: Threading!!!!
        from PyQt6.QtWidgets import QApplication
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        try:
            client = FreesoundClient()
            results = client.search_sounds(query)
            
            if not results:
                 item = QListWidgetItem("No results found.")
                 self.online_list.addItem(item)
                 
            for i, res in enumerate(results):
                name = res.get("name", "Unknown")
                duration = res.get("duration", 0)
                previews = res.get("previews", {})
                preview_url = previews.get("preview-hq-mp3")
                tags = res.get("tags", []) # Not requesting tags yet? updated fields?
                # fields request in client was: id,name,previews,duration,username,type,images
                username = res.get("username", "")
                
                item = QListWidgetItem(self.online_list)
                item.setSizeHint(QSize(0, 45))
                
                row = OnlineTrackRow(i+1, name, duration, f"User: {username}")
                
                # Connect Play
                row.play_btn.clicked.connect(lambda ch, url=preview_url, t=name: self.play_preview(url, t))
                
                # Connect Download
                row.download_btn.clicked.connect(lambda ch, url=preview_url, t=name: self.download_online_sound(url, t))
                
                self.online_list.setItemWidget(item, row)
                
        except Exception as e:
            print(f"Search error: {e}")
            QMessageBox.critical(self, "Error", f"Search failed: {e}")
            
        finally:
            QApplication.restoreOverrideCursor()
            
    def play_preview(self, url, title):
        if not url: return
        print(f"Previewing: {url}")
        
        # STREAMING FIX: Download to temp cache first
        import os
        import hashlib
        
        # Create cache dir
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Generate clean filename
        hash_name = hashlib.md5(url.encode()).hexdigest()
        filename = f"{hash_name}.mp3"
        local_path = os.path.join(cache_dir, filename)
        
        # Check if exists
        if not os.path.exists(local_path):
            from PyQt6.QtWidgets import QApplication
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:
                from utils.freesound_client import FreesoundClient
                client = FreesoundClient()
                print(f"Caching preview to {local_path}...")
                success = client.download_preview(url, local_path)
                if not success:
                    QMessageBox.warning(self, "Preview Error", "Could not cache preview.")
                    QApplication.restoreOverrideCursor()
                    return
            except Exception as e:
                print(f"Cache error: {e}")
                QApplication.restoreOverrideCursor()
                return
            finally:
                QApplication.restoreOverrideCursor()
        
        # Play Local File
        self.player.load(local_path)
        self.player.play()
        
        # Load Waveform for Preview
        try:
            from utils.audio_loader import load_waveform_data
            from utils.metadata_reader import get_track_metadata
            data, _, _ = load_waveform_data(local_path, points=800)
            meta = get_track_metadata(local_path)
            duration = meta.get("duration", 0)
        except Exception as e:
            print(f"Waveform error: {e}")
            data = None
            duration = 0
            
        self.playback_bar.set_track_info(f"PREVIEW: {title}", data, local_path, duration)
        self.playback_bar.set_playing_state(True)
            
    def download_online_sound(self, url, name):
        if not url: return
        
        # Target: Current Vault Folder or Downloads
        target_dir = fops.get_vault_path() # Default root vault
        current = self.library_tree.currentItem()
        if current:
            path = current.data(0, Qt.ItemDataRole.UserRole)
            if path and os.path.isdir(path):
                target_dir = path
        
        # Sanitize filename and apply "WC - " prefix for standardization
        import re
        safe_name = re.sub(r'[\\/*?:"<>|]', "", name).upper()
        filename = f"WC - {safe_name}.mp3"
        target_path = os.path.join(target_dir, filename)
        
        # Download
        from PyQt6.QtWidgets import QApplication
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        try:
            from utils.freesound_client import FreesoundClient
            client = FreesoundClient()
            success = client.download_preview(url, target_path)
            
            if success:
                # REFRESH UI
                from utils.library_cache import invalidate_cache
                invalidate_cache(target_dir)
                
                # If we are currently viewing this folder, refresh the list
                if hasattr(self, 'current_scan_path'):
                    if os.path.normpath(self.current_scan_path) == os.path.normpath(target_dir):
                        self.scan_and_display_files(target_dir)
                
                QMessageBox.information(self, "Downloaded", f"Guardado con éxito en:\n{target_path}")
                self.statusBar().showMessage(f"Descargado: {filename}", 3000)
            else:
                QMessageBox.warning(self, "Error", "Download failed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Download error: {e}")
        finally:
            QApplication.restoreOverrideCursor()

