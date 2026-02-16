from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QListWidget, QFileDialog, QListWidgetItem, 
                             QSplitter, QTreeWidget, QTreeWidgetItem, QMessageBox, QLabel, QMenu,
                             QTabWidget, QLineEdit, QStackedWidget, QTableView, QHeaderView, QInputDialog, QApplication)
from PyQt6.QtGui import QAction, QIcon, QCursor, QColor, QBrush, QPixmap, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, QSize, QDir, QTimer, QUrl, pyqtSignal, QPoint
from ui.playback_bar import PlaybackBar
import utils.file_ops as fops
from ui.library_model import LibraryModel
from ui.track_delegate import TrackDelegate
from utils.scanner_thread import ScannerThread
from utils.library_cache import get_cached_folder_data, save_folder_to_cache
import os

class AudioPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.settings = main_window.settings
        self.player = main_window.player
        self.localizer = main_window.localizer
        self.fav_manager = main_window.fav_manager
        
        # Connect Player Signals
        self.player.position_changed.connect(self.on_player_position_changed)
        self.player.state_changed.connect(self.on_player_state_changed)
        
        self.init_ui()
        
        # Load Vault
        self.load_vault()
        
        # Shortcuts
        self.space_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        self.space_shortcut.activated.connect(self.player.toggle_play)

    def init_ui(self):
        # Vertical Layout: [Splitter (Content)] / [PlaybackBar]
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- SPLITTER (Sidebar + List) ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sidebar
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # --- TABS: Library / Online ---
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
                min-width: 80px;
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
        self.fav_item.setForeground(0, QColor("#FFB347"))
        
        lib_layout.addWidget(self.library_tree)
        
        self.tab_idx_library = self.sidebar_tabs.addTab(tab_library, self.localizer.get("library_header").strip())
        
        # TAB 2: ONLINE (Freesound)
        tab_online = QWidget()
        online_tab_layout = QVBoxLayout(tab_online)
        lbl_intro = QLabel("Search Freesound\nin the main view ->")
        lbl_intro.setStyleSheet("color: #666; font-style: italic; margin-top: 20px;")
        lbl_intro.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        online_tab_layout.addWidget(lbl_intro)
        online_tab_layout.addStretch()
        
        self.tab_idx_online = self.sidebar_tabs.addTab(tab_online, "Online")
        
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
        
        # Local Header
        self.local_header = QWidget()
        self.local_header.setFixedHeight(30)
        self.local_header.setStyleSheet("background-color: #1a1a1a; border-bottom: 1px solid #333;")
        lh_layout = QHBoxLayout(self.local_header)
        lh_layout.setContentsMargins(0, 0, 0, 0)
        lh_layout.setSpacing(0)
        
        def add_h_lbl(layout, text, width=None, align=Qt.AlignmentFlag.AlignLeft, expand=False):
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #888; font-size: 11px; font-weight: bold; text-transform: uppercase;")
            lbl.setContentsMargins(5, 0, 5, 0)
            
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

        for i, key in enumerate(LibraryColumns.HEADERS_KEYS):
            header_text = self.localizer.get(key)
            width = LibraryColumns.WIDTHS[i]
            align = Qt.AlignmentFlag.AlignLeft
            expand = False
            
            if i == LibraryColumns.INDEX: align = Qt.AlignmentFlag.AlignRight
            elif i in (LibraryColumns.FAV, LibraryColumns.CHANNELS, LibraryColumns.FORMAT, LibraryColumns.DURATION): 
                align = Qt.AlignmentFlag.AlignCenter
            
            add_h_lbl(lh_layout, header_text, width, align, expand)

        lh_layout.addStretch()
        header_spacer = QWidget()
        header_spacer.setFixedWidth(15) 
        lh_layout.addWidget(header_spacer)

        self.local_header_labels = [c for c in self.local_header.findChildren(QLabel)]
        local_layout.addWidget(self.local_header)
        
        # --- TABLE VIEW ---
        self.library_model = LibraryModel(self, self.localizer)
        self.track_delegate = TrackDelegate(self)
        
        self.track_view = QTableView()
        self.track_view.setModel(self.library_model)
        self.track_view.setItemDelegate(self.track_delegate)
        
        self.track_view.setShowGrid(False)
        self.track_view.verticalHeader().setVisible(False)
        self.track_view.horizontalHeader().setVisible(False)
        
        self.track_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.track_view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.track_view.setAlternatingRowColors(False)
        self.track_view.setStyleSheet("background-color: #121212; border: none;")
        self.track_view.setVerticalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.track_view.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        
        self.track_view.setDragEnabled(True)
        self.track_view.setDragDropMode(QTableView.DragDropMode.DragOnly)
        
        header = self.track_view.horizontalHeader()
        for i in range(LibraryColumns.COUNT):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
            header.resizeSection(i, LibraryColumns.WIDTHS[i])
            
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
        self.search_area = QWidget()
        self.search_area.setStyleSheet("background-color: #1f1f1f; border-bottom: 1px solid #333;")
        search_area_layout = QHBoxLayout(self.search_area)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Freesound...")
        self.search_input.setStyleSheet("background-color: #333; color: white; border: 1px solid #444; padding: 5px; border-radius: 3px;")
        self.search_input.returnPressed.connect(self.search_freesound)
        
        self.btn_search = QPushButton("SEARCH")
        self.btn_search.setStyleSheet("QPushButton { background-color: #D75239; color: white; border: none; padding: 6px 15px; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #ff6d50; }")
        self.btn_search.clicked.connect(self.search_freesound)
        
        search_area_layout.addWidget(self.search_input)
        search_area_layout.addWidget(self.btn_search)
        online_layout.addWidget(self.search_area)
        
        # Online Header
        self.online_header = QWidget()
        self.online_header.setFixedHeight(30)
        self.online_header.setStyleSheet("background-color: #1a1a1a; border-bottom: 1px solid #333;")
        oh_layout = QHBoxLayout(self.online_header)
        oh_layout.setContentsMargins(0, 0, 0, 0)
        oh_layout.setSpacing(0)
        self.online_header_labels = []

        for i, key in enumerate(LibraryColumns.HEADERS_KEYS):
            header_text = self.localizer.get(key)
            width = LibraryColumns.WIDTHS[i]
            align = Qt.AlignmentFlag.AlignLeft
            expand = False
            
            if i == LibraryColumns.INDEX: align = Qt.AlignmentFlag.AlignRight
            elif i in (LibraryColumns.FAV, LibraryColumns.CHANNELS, LibraryColumns.FORMAT, LibraryColumns.DURATION): 
                align = Qt.AlignmentFlag.AlignCenter
            
            lbl = QLabel(header_text)
            lbl.setProperty("key", key)
            lbl.setStyleSheet("color: #888; font-size: 11px; font-weight: bold; text-transform: uppercase;")
            lbl.setContentsMargins(5, 0, 5, 0)
            if width:
                if expand: lbl.setMinimumWidth(width)
                else: lbl.setFixedWidth(width)
            lbl.setAlignment(align | Qt.AlignmentFlag.AlignVCenter)
            oh_layout.addWidget(lbl)
            self.online_header_labels.append(lbl)
        oh_layout.setSpacing(0)
        
        add_h_lbl(oh_layout, "#", 40, Qt.AlignmentFlag.AlignRight)
        add_h_lbl(oh_layout, "", 25)
        add_h_lbl(oh_layout, "Name", 200)
        add_h_lbl(oh_layout, "Format", 60, Qt.AlignmentFlag.AlignCenter)
        add_h_lbl(oh_layout, "Duration", 70, Qt.AlignmentFlag.AlignRight)
        add_h_lbl(oh_layout, "Description", 150)
        add_h_lbl(oh_layout, "Action", expand=True) 

        oh_spacer = QWidget()
        oh_spacer.setFixedWidth(15)
        oh_layout.addWidget(oh_spacer)
        
        online_layout.addWidget(self.online_header)
        
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

    def load_vault(self):
        fops.ensure_vault_exists()
        audio_path = fops.get_audio_path()
        if os.path.exists(audio_path):
            self.add_folder_to_library(audio_path)

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
        try:
            if hasattr(self, 'scanner_thread') and self.scanner_thread.isRunning():
                self.scanner_thread.stop()
                
            self.library_model.clear()
            paths = self.fav_manager.get_all()
            if not paths: 
                return
            
            valid_paths = [p for p in paths if os.path.exists(p)]
            if not valid_paths:
                return

            self.scanner_thread = ScannerThread(file_paths=valid_paths)
            self.scanner_thread.batch_found.connect(self.on_scan_batch)
            self.scanner_thread.finished_scan.connect(self.on_scan_finished)
            self.scanner_thread.start()
        except Exception as e:
            print(f"Error loading favorites: {e}")

    def scan_and_display_files(self, folder_path):
        if hasattr(self, 'scanner_thread') and self.scanner_thread.isRunning():
            self.scanner_thread.stop()
            
        self.library_model.clear()
        
        cached_tracks = get_cached_folder_data(folder_path)
        if cached_tracks:
            print(f"Loading {folder_path} from cache...")
            import numpy as np
            for t in cached_tracks:
                t["waveform"] = np.array(t["waveform"], dtype=np.float32)
                t["is_favorite"] = self.fav_manager.is_favorite(t["path"])
            self.library_model.add_tracks(cached_tracks)
            return

        print(self.localizer.get("status_loading").format(folder_path))
        self.current_scan_path = folder_path
        self.current_scan_results = []
        
        self.scanner_thread = ScannerThread(folder_path)
        self.scanner_thread.batch_found.connect(self.on_scan_batch_with_cache)
        self.scanner_thread.finished_scan.connect(self.on_scan_finished_with_cache)
        self.scanner_thread.start()

    def on_scan_batch_with_cache(self, tracks):
        for track in tracks:
            track["is_favorite"] = self.fav_manager.is_favorite(track["path"])
            self.current_scan_results.append(track)
        self.library_model.add_tracks(tracks)

    def on_scan_finished_with_cache(self, count):
        if hasattr(self, 'current_scan_path') and self.current_scan_results:
            save_folder_to_cache(self.current_scan_path, self.current_scan_results)
        self.on_scan_finished(count)
        
    def on_scan_batch(self, tracks):
        for track in tracks:
            track["is_favorite"] = self.fav_manager.is_favorite(track["path"])
        self.library_model.add_tracks(tracks)
        
    def on_scan_finished(self, count):
        print(self.localizer.get("status_loaded").format(count))
        
    def on_track_clicked(self, index):
        try:
            track = self.library_model.get_track_at(index.row())
            if not track: return

            if index.column() == self.library_model.COL_FAV:
                path = track.get("path")
                is_fav = self.fav_manager.toggle(path)
                track["is_favorite"] = is_fav
                self.library_model.dataChanged.emit(index, index)
                return

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
                    track = self.library_model.get_track_at(index.row())
                    if track:
                        self.play_track(track["path"], track["title"], track["waveform"], track["duration"])
        except Exception as e:
            print(f"Error in on_track_clicked: {e}")

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
            QMessageBox.critical(self, self.localizer.get("msg_playback_error"), f"{e}")

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
                sizes = [int(s) for s in saved_state]
                self.main_splitter.setSizes(sizes)
            except:
                pass 

    def save_state(self):
        sizes = self.main_splitter.sizes()
        self.settings.setValue("splitter_sizes", [str(s) for s in sizes])

    # --- ACTION HANDLERS ---
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
        target_item = parent_item
        if not target_item:
            target_item = self.library_tree.currentItem()
        if not target_item and self.library_tree.topLevelItemCount() > 0:
            target_item = self.library_tree.topLevelItem(0)
        
        if not target_item:
            QMessageBox.warning(self, self.localizer.get("window_title"), self.localizer.get("msg_import_first"))
            return

        target_path = target_item.data(0, Qt.ItemDataRole.UserRole)
        if not os.path.isdir(target_path):
             QMessageBox.warning(self, self.localizer.get("msg_error"), self.localizer.get("msg_invalid_folder"))
             return 
            
        text, ok = QInputDialog.getText(self, self.localizer.get("ctx_new_folder"), self.localizer.get("msg_new_name"))
        if ok and text:
            try:
                new_path = fops.create_new_folder(target_path, text)
                name = os.path.basename(new_path)
                new_item = QTreeWidgetItem(target_item)
                new_item.setText(0, name)
                new_item.setData(0, Qt.ItemDataRole.UserRole, new_path)
                target_item.setExpanded(True)
            except Exception as e:
                QMessageBox.critical(self, self.localizer.get("msg_error"), str(e))

    def action_rename_folder(self, item):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        old_name = item.text(0)
        text, ok = QInputDialog.getText(self, self.localizer.get("msg_rename"), self.localizer.get("msg_new_name"), text=old_name)
        if ok and text and text != old_name:
            try:
                new_path = fops.rename_item(path, text)
                item.setText(0, text)
                item.setData(0, Qt.ItemDataRole.UserRole, new_path)
            except Exception as e:
                QMessageBox.critical(self, self.localizer.get("msg_error"), str(e))

    def action_delete_folder(self, item):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        msg = self.localizer.get("msg_confirm_delete").format(item.text(0))
        reply = QMessageBox.question(self, self.localizer.get("ctx_delete"), msg,
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                fops.delete_item(path)
                parent = item.parent()
                if parent:
                    parent.removeChild(item)
                else:
                    index = self.library_tree.indexOfTopLevelItem(item)
                    self.on_category_selected(self.library_tree.currentItem(), 0)
            except Exception as e:
                QMessageBox.critical(self, self.localizer.get("msg_error"), str(e))

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

        path = track["path"]
        old_name = track["title"]
        title = self.localizer.get("msg_rename")
        label = self.localizer.get("msg_new_name")
        text, ok = QInputDialog.getText(self, title, label, text=old_name)
        if ok and text and text != old_name:
            try:
                new_path = fops.rename_item(path, text)
                self.library_model.update_track_info(index.row(), {"path": new_path, "title": text})
            except Exception as e:
                 QMessageBox.critical(self, self.localizer.get("msg_error"), str(e))

    def action_delete_file(self, index, track):
        path = track["path"]
        title = self.localizer.get("ctx_delete")
        msg = self.localizer.get("msg_confirm_delete").format(track['title'])
        reply = QMessageBox.question(self, title, msg,
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                fops.delete_item(path)
                self.library_model.removeRow(index.row())
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def on_tab_changed(self, index):
        self.right_stack.setCurrentIndex(index)
        if index == 1:
            self.search_input.setFocus()

    def search_freesound(self):
        from utils.freesound_client import FreesoundClient
        from ui.online_track_row import OnlineTrackRow
        
        query = self.search_input.text()
        if not query: return
        
        self.online_list.clear()
        
        try:
            from deep_translator import GoogleTranslator
            translated = GoogleTranslator(source='auto', target='en').translate(query)
            if translated and translated.lower() != query.lower():
                self.search_input.setText(translated) 
                query = translated 
        except Exception as e:
            print(f"Translation failed: {e}")

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        try:
            client = FreesoundClient()
            results = client.search_sounds(query)
            
            if not results:
                 item = QListWidgetItem(self.localizer.get("msg_no_results"))
                 self.online_list.addItem(item)
                 
            for i, res in enumerate(results):
                name = res.get("name", "Unknown")
                duration = res.get("duration", 0)
                previews = res.get("previews", {})
                preview_url = previews.get("preview-hq-mp3")
                username = res.get("username", "")
                
                item = QListWidgetItem(self.online_list)
                item.setSizeHint(QSize(0, 45))
                row = OnlineTrackRow(i+1, name, duration, f"User: {username}")
                row.play_btn.clicked.connect(lambda ch, url=preview_url, t=name: self.play_preview(url, t))
                row.download_btn.clicked.connect(lambda ch, url=preview_url, t=name: self.download_online_sound(url, t))
                self.online_list.setItemWidget(item, row)
                
        except Exception as e:
            QMessageBox.critical(self, self.localizer.get("msg_error"), f"{self.localizer.get('msg_search_error')} {e}")
        finally:
            QApplication.restoreOverrideCursor()

    def play_preview(self, url, title):
        if not url: return
        import hashlib
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        hash_name = hashlib.md5(url.encode()).hexdigest()
        filename = f"{hash_name}.mp3"
        local_path = os.path.join(cache_dir, filename)
        
        if not os.path.exists(local_path):
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:
                from utils.freesound_client import FreesoundClient
                client = FreesoundClient()
                success = client.download_preview(url, local_path)
                if not success:
                    QMessageBox.warning(self, self.localizer.get("msg_error"), self.localizer.get("msg_download_failed"))
                    return
            except Exception as e:
                return
            finally:
                QApplication.restoreOverrideCursor()
        
        self.player.load(local_path)
        self.player.play()
        
        try:
            from utils.audio_loader import load_waveform_data
            from utils.metadata_reader import get_track_metadata
            data, _, _ = load_waveform_data(local_path, points=800)
            meta = get_track_metadata(local_path)
            duration = meta.get("duration", 0)
        except Exception as e:
            data = None
            duration = 0
        self.playback_bar.set_track_info(f"PREVIEW: {title}", data, local_path, duration)
        self.playback_bar.set_playing_state(True)

    def retranslate_ui(self):
        # 1. Sidebar Tabs
        self.sidebar_tabs.setTabText(self.tab_idx_library, self.localizer.get("library_header").strip())
        self.sidebar_tabs.setTabText(self.tab_idx_online, self.localizer.get("tab_online") if self.localizer.get("tab_online") != "tab_online" else "Online")

        # 2. Tree Item
        if hasattr(self, 'fav_item'):
            self.fav_item.setText(0, "★ " + self.localizer.get("col_genre").replace("Genre", "Favorites"))

        # 3. Model Headers
        self.library_model.set_localizer(self.localizer)
        
        # 4. Header Labels (Local & Online)
        from constants import LibraryColumns
        for i, lbl in enumerate(self.local_header_labels):
            if i < len(LibraryColumns.HEADERS_KEYS):
                lbl.setText(self.localizer.get(LibraryColumns.HEADERS_KEYS[i]))
        
        for lbl in self.online_header_labels:
            key = lbl.property("key")
            if key:
                lbl.setText(self.localizer.get(key))

        # 5. Search Area
        self.search_input.setPlaceholderText(self.localizer.get("placeholder_search_audio") if self.localizer.get("placeholder_search_audio") != "placeholder_search_audio" else "Search Freesound...")
        self.btn_search.setText(self.localizer.get("btn_search") if self.localizer.get("btn_search") != "btn_search" else "SEARCH")

    def apply_theme(self, t):
        # 1. Main Styles
        self.setStyleSheet(f"background-color: {t.get('bg_main')}; color: {t.get('text_main')};")
        
        # 2. Tabs
        self.sidebar_tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: none; }}
            QTabBar::tab {{
                background: {t.get('bg_toolbar')};
                color: {t.get('text_secondary')};
                padding: 8px 15px;
                border: 1px solid {t.get('border')};
                border-bottom: 2px solid {t.get('border')};
                min-width: 80px;
            }}
            QTabBar::tab:selected {{
                color: {t.get('accent')};
                background: {t.get('bg_secondary')};
                border-bottom: 2px solid {t.get('accent')};
                font-weight: bold;
            }}
        """)
        
        # 3. Tree
        self.library_tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {t.get('bg_secondary')};
                border: none;
                color: {t.get('text_main')};
                outline: none;
            }}
            QTreeWidget::item {{ padding: 4px; }}
            QTreeWidget::item:selected {{ background-color: {t.get('accent')}; color: white; }}
            QTreeWidget::item:hover {{ background-color: {t.get('bg_button')}; }}
        """)
        
        # 4. Table & Lists
        self.track_view.setStyleSheet(f"background-color: {t.get('bg_main')}; border: none;")
        self.online_list.setStyleSheet(f"background-color: {t.get('bg_main')}; border: none;")
        
        # 5. Headers
        header_style = f"background-color: {t.get('bg_secondary')}; border-bottom: 1px solid {t.get('border')};"
        if hasattr(self, 'local_header'): self.local_header.setStyleSheet(header_style)
        if hasattr(self, 'online_header'): self.online_header.setStyleSheet(header_style)
        if hasattr(self, 'search_area'): self.search_area.setStyleSheet(header_style)
        
        for lbl in self.local_header_labels + self.online_header_labels:
            lbl.setStyleSheet(f"color: {t.get('text_secondary')}; font-size: 11px; font-weight: bold; text-transform: uppercase;")

        # 6. Inputs & Buttons
        self.search_input.setStyleSheet(f"background-color: {t.get('bg_button')}; color: {t.get('text_main')}; border: 1px solid {t.get('border')}; padding: 5px; border-radius: 3px;")
        
        # 7. Delegate & Playback Bar
        self.track_delegate.apply_theme(t)
        self.track_view.viewport().update()
        self.playback_bar.apply_theme(t)
    def download_online_sound(self, url, name):
        if not url: return
        target_dir = fops.get_vault_path()
        current = self.library_tree.currentItem()
        if current:
            path = current.data(0, Qt.ItemDataRole.UserRole)
            if path and os.path.isdir(path):
                target_dir = path
        
        import re
        safe_name = re.sub(r'[\\/*?:"<>|]', "", name).upper()
        filename = f"WC - {safe_name}.mp3"
        target_path = os.path.join(target_dir, filename)
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            from utils.freesound_client import FreesoundClient
            client = FreesoundClient()
            success = client.download_preview(url, target_path)
            
            if success:
                from utils.library_cache import invalidate_cache
                invalidate_cache(target_dir)
                if hasattr(self, 'current_scan_path'):
                    if os.path.normpath(self.current_scan_path) == os.path.normpath(target_dir):
                        self.scan_and_display_files(target_dir)
                QMessageBox.information(self, "Downloaded", f"Guardado con éxito en:\n{target_path}")
            else:
                QMessageBox.warning(self, "Error", "Download failed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Download error: {e}")
        finally:
            QApplication.restoreOverrideCursor()
