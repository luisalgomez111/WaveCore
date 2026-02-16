from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, 
                             QListWidgetItem, QLabel, QPushButton, QFileDialog, 
                             QTabWidget, QLineEdit, QApplication, QMessageBox, QFrame, QScrollArea, QSizePolicy, QButtonGroup, QMenu, QInputDialog)
from PyQt6.QtCore import Qt, QSize, QTimer, QUrl, QMimeData, QPoint, QThread, pyqtSignal, QRect
from PyQt6.QtGui import QIcon, QDrag, QPixmap, QImage, QPainter
from ui.modules.VideoPlayerWidget import VideoPlayerWidget
from utils.pixabay_client import PixabayClient
from utils.pexels_client import PexelsClient
import utils.file_ops as fops
from utils.video_utils import VideoMetadataExtractor
import os
import requests

class ThumbnailLoader(QThread):
    thumbnail_loaded = pyqtSignal(QListWidgetItem, QPixmap)

    def __init__(self, item, url):
        super().__init__()
        self.item = item
        self.url = url

    def run(self):
        try:
            response = requests.get(self.url, timeout=5)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.thumbnail_loaded.emit(self.item, pixmap)
        except:
            pass

class DraggableVideoListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item: return
        
        path = item.data(Qt.ItemDataRole.UserRole)
        # Only drag local files
        if not path or not os.path.exists(path): return
        
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(path)])
        drag.setMimeData(mime_data)
        
        pixmap = item.icon().pixmap(160, 90)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
        
        drag.exec(Qt.DropAction.CopyAction)

class AspectRatioWidget(QWidget):
    def __init__(self, widget, ratio=16/9, offset=0, parent=None):
        super().__init__(parent)
        self.widget = widget
        self.ratio = ratio
        self.offset = offset
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.widget)
        
    def resizeEvent(self, event):
        w = event.size().width()
        h = int(w / self.ratio) + self.offset
        self.widget.setFixedHeight(h)
        super().resizeEvent(event)

class VideoPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.localizer = main_window.localizer
        self.pixabay = PixabayClient()
        self.pexels = PexelsClient()
        self.metadata_extractor = VideoMetadataExtractor()
        
        self.loader_threads = [] 
        self.current_page = 1
        self.current_query = ""
        
        self.init_ui()
        self.load_library()
        
    def load_library(self):
        fops.ensure_vault_exists()
        video_path = fops.get_video_path()
        if os.path.exists(video_path):
            with os.scandir(video_path) as it:
                for entry in it:
                     if entry.is_file():
                        ext = os.path.splitext(entry.name)[1].lower()
                        if ext in ('.mp4', '.mov', '.avi', '.mkv'):
                            self.add_video_to_grid(entry.path)
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: #333; }")
        
        # --- LEFT: TABS ---
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background: #1f1f1f;
                color: #888;
                padding: 8px 20px;
                border-bottom: 2px solid transparent;
            }
            QTabBar::tab:selected {
                color: #D75239;
                border-bottom: 2px solid #D75239;
                background: #1a1a1a;
                font-weight: bold;
            }
        """)
        
        # TAB 1: LOCAL
        tab_local = QWidget()
        local_layout = QVBoxLayout(tab_local)
        local_layout.setContentsMargins(0, 0, 0, 0)
        
        local_toolbar = QWidget()
        local_toolbar.setObjectName("toolbar")
        local_toolbar.setFixedHeight(40)
        local_toolbar.setStyleSheet("background-color: #1f1f1f; border-bottom: 1px solid #333;")
        self.local_toolbar = local_toolbar
        lt_layout = QHBoxLayout(local_toolbar)
        
        self.btn_import = QPushButton("Import Footage")
        self.btn_import.setStyleSheet("background-color: #333; color: white; border: none; padding: 5px 10px;")
        self.btn_import.clicked.connect(self.import_footage)
        lt_layout.addWidget(self.btn_import)
        lt_layout.addStretch()
        local_layout.addWidget(local_toolbar)
        
        self.video_grid = DraggableVideoListWidget()
        self.video_grid.setViewMode(QListWidget.ViewMode.IconMode)
        self.video_grid.setIconSize(QSize(160, 90))
        self.video_grid.setGridSize(QSize(180, 130))
        self.video_grid.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.video_grid.setSpacing(10)
        self.video_grid.setWordWrap(True)
        self.video_grid.setStyleSheet(self._grid_style())
        self.video_grid.itemClicked.connect(self.on_video_selected)
        self.video_grid.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.video_grid.customContextMenuRequested.connect(self.open_video_menu)
        local_layout.addWidget(self.video_grid)
        
        self.tabs.addTab(tab_local, "Local Library")
        
        # TAB 2: ONLINE
        tab_online = QWidget()
        online_layout = QVBoxLayout(tab_online)
        online_layout.setContentsMargins(0, 0, 0, 0)
        
        search_bar = QWidget()
        search_bar.setObjectName("searchBar")
        search_bar.setFixedHeight(50)
        search_bar.setStyleSheet("background-color: #1f1f1f; border-bottom: 1px solid #333;")
        self.search_bar = search_bar
        sb_layout = QHBoxLayout(search_bar)
        
        # Custom Toggle for Source
        self.source_group = QButtonGroup(self)
        self.btn_pixabay = QPushButton("Pixabay")
        self.btn_pixabay.setCheckable(True)
        self.btn_pixabay.setChecked(True)
        self.btn_pixabay.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pixabay.setFixedHeight(30)
        
        self.btn_pexels = QPushButton("Pexels")
        self.btn_pexels.setCheckable(True)
        self.btn_pexels.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pexels.setFixedHeight(30)
        
        self.source_group.addButton(self.btn_pixabay)
        self.source_group.addButton(self.btn_pexels)
        self.source_group.buttonClicked.connect(self.on_provider_changed)
        
        # Style for toggles
        toggle_style = """
            QPushButton {
                background-color: #333;
                color: #888;
                border: none;
                padding: 5px 15px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:checked {
                background-color: #D75239;
                color: white;
            }
            QPushButton:hover:!checked {
                background-color: #444;
            }
        """
        self.btn_pixabay.setStyleSheet(toggle_style)
        self.btn_pexels.setStyleSheet(toggle_style)
        
        sb_layout.addWidget(self.btn_pixabay)
        sb_layout.addWidget(self.btn_pexels)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Videos...")
        self.search_input.setStyleSheet("background-color: #333; color: white; border: 1px solid #444; padding: 8px; border-radius: 4px;")
        self.search_input.returnPressed.connect(self.search_online)
        
        self.btn_search = QPushButton("SEARCH")
        self.btn_search.setStyleSheet("background-color: #D75239; color: white; border: none; padding: 8px 15px; border-radius: 4px; font-weight: bold;")
        self.btn_search.clicked.connect(self.search_online)
        
        sb_layout.addWidget(self.search_input)
        sb_layout.addWidget(self.btn_search)
        online_layout.addWidget(search_bar)
        
        self.online_grid = QListWidget()
        self.online_grid.setViewMode(QListWidget.ViewMode.IconMode)
        self.online_grid.setIconSize(QSize(160, 90))
        self.online_grid.setGridSize(QSize(180, 130))
        self.online_grid.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.online_grid.setSpacing(10)
        self.online_grid.setWordWrap(True)
        self.online_grid.setStyleSheet(self._grid_style())
        self.online_grid.itemClicked.connect(self.on_online_video_selected)
        online_layout.addWidget(self.online_grid)
        
        # Load More Button
        self.btn_load_more = QPushButton("Load More Results")
        self.btn_load_more.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_load_more.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: #aaa;
                border: 1px solid #444;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #444;
                color: white;
            }
        """)
        self.btn_load_more.clicked.connect(self.load_more_results)
        self.btn_load_more.setVisible(False)
        online_layout.addWidget(self.btn_load_more)
        
        self.tabs.addTab(tab_online, "Downloads")
        
        self.splitter.addWidget(self.tabs)
        
        # --- RIGHT: INSPECTOR ---
        self.inspector = QWidget()
        self.inspector.setObjectName("inspector")
        self.inspector.setMinimumWidth(350)
        self.inspector.setStyleSheet("background-color: #1a1a1a; border-left: 1px solid #333;")
        ins_layout = QVBoxLayout(self.inspector)
        ins_layout.setContentsMargins(0, 0, 0, 0)
        ins_layout.setSpacing(0)
        
        # 1. Video Player
        self.video_player = VideoPlayerWidget()
        self.player_container = AspectRatioWidget(self.video_player, ratio=16/9, offset=120)
        ins_layout.addWidget(self.player_container)
        
        # 2. Metadata
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: #1a1a1a;")
        
        self.meta_container = QWidget()
        meta_layout = QVBoxLayout(self.meta_container)
        meta_layout.setContentsMargins(15, 15, 15, 15)
        meta_layout.setSpacing(10)
        
        self.lbl_inspector_header = QLabel("METADATA")
        self.lbl_inspector_header.setStyleSheet("color: #666; font-size: 11px; font-weight: bold; margin-bottom: 5px;")
        meta_layout.addWidget(self.lbl_inspector_header)
        
        self.lbl_title = self._create_meta_label("Filename: -")
        self.lbl_duration = self._create_meta_label("Duration: -")
        self.lbl_res = self._create_meta_label("Resolution: -")
        self.lbl_fps = self._create_meta_label("FPS: -")
        self.lbl_size = self._create_meta_label("Size: -")
        self.lbl_path = self._create_meta_label("Path: -")
        self.lbl_path.setWordWrap(True)
        
        for l in [self.lbl_title, self.lbl_duration, self.lbl_res, self.lbl_fps, self.lbl_size, self.lbl_path]:
            meta_layout.addWidget(l)
            
        self.btn_download = QPushButton("DOWNLOAD TO LIBRARY")
        self.btn_download.setStyleSheet("background-color: #D75239; color: white; padding: 10px; border-radius: 4px; font-weight: bold; margin-top: 10px;")
        self.btn_download.setVisible(False)
        self.btn_download.clicked.connect(self.download_current_video)
        meta_layout.addWidget(self.btn_download)
        
        meta_layout.addStretch()
        scroll.setWidget(self.meta_container)
        
        ins_layout.addWidget(scroll)
        self.splitter.addWidget(self.inspector)
        self.splitter.setSizes([800, 350])
        layout.addWidget(self.splitter)

    def _grid_style(self, t=None):
        if not t:
            return """
                QListWidget { background-color: #121212; border: none; padding: 10px; }
                QListWidget::item { background-color: #1a1a1a; border-radius: 5px; color: #ddd; }
                QListWidget::item:selected { background-color: #D75239; color: white; }
                QListWidget::item:hover { background-color: #333; }
            """
        return f"""
            QListWidget {{
                background-color: {t.get('bg_main')};
                border: none;
                outline: none;
                color: {t.get('text_main')};
            }}
            QListWidget::item {{
                color: {t.get('text_main')};
                background-color: {t.get('bg_secondary')};
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 5px;
                border: 1px solid {t.get('border')};
            }}
            QListWidget::item:selected {{
                background-color: {t.get('accent')};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {t.get('bg_button')};
            }}
        """

    def _create_meta_label(self, text):
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        # Style will be handled by apply_theme
        return lbl

    def import_footage(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Import Video", "", "Video Files (*.mp4 *.mov *.avi *.mkv)")
        if files:
            for f in files:
                self.add_video_to_grid(f)

    def add_video_to_grid(self, path):
        name = os.path.basename(path)
        item = QListWidgetItem(name)
        item.setData(Qt.ItemDataRole.UserRole, path)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            meta = self.metadata_extractor.get_metadata(path)
            thumb_path = meta.get("thumbnail_path")
            if thumb_path and os.path.exists(thumb_path):
                pixmap = QPixmap(thumb_path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(160, 90, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                    item.setIcon(QIcon(scaled))
        finally:
            QApplication.restoreOverrideCursor()
        self.video_grid.addItem(item)

    def on_video_selected(self, item):
        selected_count = len(self.video_grid.selectedItems())
        if selected_count > 1:
            self.lbl_title.setText(f"{selected_count} Videos Selected")
            self.lbl_duration.setText("-")
            self.lbl_res.setText("-")
            self.lbl_size.setText("-")
            self.lbl_path.setText("-")
            self.btn_download.setVisible(False)
            return

        path = item.data(Qt.ItemDataRole.UserRole)
        self.btn_download.setVisible(False)
        if path and isinstance(path, str) and os.path.exists(path):
            self.update_inspector(path, is_online=False)
            self.video_player.load_video(path)

    def update_inspector(self, data, is_online=False):
        if not is_online:
            path = data
            file_size = os.path.getsize(path) / (1024 * 1024)
            meta = self.metadata_extractor.get_metadata(path)
            self.lbl_title.setText(f"Filename: {os.path.basename(path)}")
            self.lbl_duration.setText(f"Duration: {meta.get('duration', 0):.2f}s")
            self.lbl_res.setText(f"Resolution: {meta.get('width', '?')}x{meta.get('height', '?')}")
            self.lbl_fps.setText(f"FPS: {meta.get('fps', 0):.2f}")
            self.lbl_size.setText(f"Size: {file_size:.2f} MB")
            self.lbl_path.setText(f"Path: {path}")
        else:
            hit = data
            source = hit.get('_source', 'Pixabay')
            if source == 'Pixabay':
                videos = hit.get("videos", {})
                medium = videos.get("medium", {})
                self.lbl_title.setText(f"ID: {hit.get('id')}")
                self.lbl_duration.setText(f"Duration: {hit.get('duration')}s")
                self.lbl_res.setText(f"Resolution: {medium.get('width')}x{medium.get('height')}")
                self.lbl_size.setText(f"Size: {medium.get('size', 0) / (1024 * 1024):.2f} MB")
                self.lbl_path.setText(f"Source: Pixabay (User: {hit.get('user')})")
                self.current_download_url = medium.get("url")
            else: # Pexels
                files = hit.get("video_files", [])
                best_file = next((f for f in files if f.get('quality') == 'hd' and f.get('width') == 1920), files[0] if files else {})
                self.lbl_title.setText(f"ID: {hit.get('id')}")
                self.lbl_duration.setText(f"Duration: {hit.get('duration')}s")
                self.lbl_res.setText(f"Resolution: {best_file.get('width')}x{best_file.get('height')}")
                self.lbl_size.setText("Size: -")
                self.lbl_path.setText(f"Source: Pexels (User: {hit.get('user', {}).get('name')})")
                self.current_download_url = best_file.get("link")
            self.lbl_fps.setText("FPS: -")
            self.btn_download.setVisible(True)
    # --- ONLINE LOGIC ---
    def on_provider_changed(self):
        self.online_grid.clear()
        self.btn_load_more.setVisible(False)
        self.current_page = 1

    def search_online(self):
        query = self.search_input.text()
        if not query: return
        self.current_query = query
        self.current_page = 1
        self.online_grid.clear()
        self.perform_online_search()

    def load_more_results(self):
        self.current_page += 1
        self.perform_online_search()

    def perform_online_search(self):
        if not self.current_query: return
        if self.btn_pixabay.isChecked(): source = "Pixabay"
        else: source = "Pexels"

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.btn_load_more.setVisible(False)

        # Auto-translate Spanish query to English for better search results
        try:
            from deep_translator import GoogleTranslator
            translated = GoogleTranslator(source='auto', target='en').translate(self.current_query)
            if translated and translated.lower() != self.current_query.lower():
                self.search_input.setText(translated)
                self.current_query = translated
        except Exception as te:
            print(f"Translation failed: {te}")

        try:
            results = []
            if source == "Pixabay":
                results = self.pixabay.search_videos(self.current_query, page=self.current_page)
            else:
                results = self.pexels.search_videos(self.current_query, page=self.current_page)
                
            if not results and self.current_page == 1:
                self.online_grid.addItem("No results found.")
            elif results:
                self.btn_load_more.setVisible(True)
            
            for hit in results:
                item = QListWidgetItem()
                thumb_url = ""
                if source == "Pixabay":
                    videos = hit.get("videos", {})
                    thumb_url = videos.get("medium", {}).get("thumbnail") or videos.get("small", {}).get("thumbnail")
                    if not thumb_url:
                        pid = hit.get("picture_id")
                        if pid: thumb_url = f"https://i.vimeocdn.com/video/{pid}_295x166.jpg"
                    item.setText(f"ID: {hit.get('id')}")
                elif source == "Pexels":
                    pictures = hit.get("video_pictures", [])
                    if pictures: thumb_url = pictures[0].get("picture")
                    item.setText(f"ID: {hit.get('id')}")

                hit['_source'] = source
                item.setData(Qt.ItemDataRole.UserRole, hit)
                if thumb_url:
                    loader = ThumbnailLoader(item, thumb_url)
                    loader.thumbnail_loaded.connect(self.on_thumbnail_loaded)
                    self.loader_threads.append(loader)
                    loader.start()
                self.online_grid.addItem(item)
        except Exception as e:
            print(f"Search Error: {e}")
        finally:
            QApplication.restoreOverrideCursor()

    def on_thumbnail_loaded(self, item, pixmap):
        scaled = pixmap.scaled(160, 90, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        item.setIcon(QIcon(scaled))
        item.setText("")

    # --- FILE MANAGEMENT ---
    def open_video_menu(self, position):
        selected_items = self.video_grid.selectedItems()
        if not selected_items: return
        
        menu = QMenu()
        if len(selected_items) == 1:
            action_rename = menu.addAction(self.localizer.get("ctx_rename_file").replace(" File", ""))
            action_rename.triggered.connect(lambda: self.rename_selected_video(selected_items[0]))
            
        action_delete = menu.addAction(self.localizer.get("ctx_delete_file").format(len(selected_items)))
        action_delete.triggered.connect(self.delete_selected_videos)
        
        menu.exec(self.video_grid.viewport().mapToGlobal(position))

    def rename_selected_video(self, item):
        old_path = item.data(Qt.ItemDataRole.UserRole)
        if not old_path or not os.path.exists(old_path): return
        
        old_name = os.path.basename(old_path)
        title = self.localizer.get("msg_rename")
        label = self.localizer.get("msg_new_name")
        text, ok = QInputDialog.getText(self, title, label, text=old_name)
        if ok and text and text != old_name:
            try:
                new_path = fops.rename_item(old_path, text)
                item.setData(Qt.ItemDataRole.UserRole, new_path)
                item.setText(text)
                self.on_video_selected(item)
            except Exception as e:
                QMessageBox.critical(self, self.localizer.get("msg_error"), str(e))

    def delete_selected_videos(self):
        items = self.video_grid.selectedItems()
        if not items: return
        
        msg = self.localizer.get("msg_confirm_delete_multi").format(len(items))
        reply = QMessageBox.question(self, self.localizer.get("ctx_delete"), 
                                     msg,
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            for item in items:
                path = item.data(Qt.ItemDataRole.UserRole)
                if path and os.path.exists(path):
                    try:
                        fops.delete_item(path)
                        self.video_grid.takeItem(self.video_grid.row(item))
                    except Exception as e:
                        print(f"Error deleting {path}: {e}")
            self.lbl_title.setText("ID: -")
            # Clear preview/player?
            self.video_player.media_player.stop()



    def on_online_video_selected(self, item):
        hit = item.data(Qt.ItemDataRole.UserRole)
        if hit:
            self.update_inspector(hit, is_online=True)
            source = hit.get('_source', 'Pixabay')
            if source == 'Pixabay':
                 videos = hit.get("videos", {})
                 url = videos.get("medium", {}).get("url") or videos.get("small", {}).get("url")
            else: # Pexels
                  files = hit.get("video_files", [])
                  best_file = next((f for f in files if f.get('file_type') == 'video/mp4'), None)
                  url = best_file.get("link") if best_file else None
            if url:
                self.video_player.media_player.setSource(QUrl(url))
                self.video_player.play_video()

    def download_current_video(self):
        current_source = "Pixabay"
        if self.online_grid.currentItem():
            hit = self.online_grid.currentItem().data(Qt.ItemDataRole.UserRole)
            current_source = hit.get('_source', 'Pixabay')

        if not hasattr(self, 'current_download_url') or not self.current_download_url: return
        url = self.current_download_url

        if not url: return
        vault_path = fops.get_video_path()
        filename = os.path.basename(url).split("?")[0]
        if not filename.endswith(".mp4"): filename += ".mp4"
        save_path = os.path.join(vault_path, filename)
        
        msg = self.localizer.get("msg_download_confirm").format(save_path)
        reply = QMessageBox.question(self, self.localizer.get("ctx_download") if self.localizer.get("ctx_download") != "ctx_download" else "Download Video", msg, 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:
                if current_source == "Pexels": success = self.pexels.download_file(url, save_path)
                else: success = self.pixabay.download_file(url, save_path)

                if success:
                    QMessageBox.information(self, self.localizer.get("msg_success"), self.localizer.get("msg_download_success"))
                    self.add_video_to_grid(save_path)
                else:
                    QMessageBox.warning(self, self.localizer.get("msg_error"), self.localizer.get("msg_download_failed"))
            finally:
                QApplication.restoreOverrideCursor()
    def retranslate_ui(self):
        # 1. Tabs
        self.tabs.setTabText(0, self.localizer.get("library_header").strip())
        self.tabs.setTabText(1, "Online")
        
        # 2. Buttons
        self.btn_import.setText(self.localizer.get("menu_import").replace("...", ""))
        self.btn_search.setText(self.localizer.get("btn_welcome_start").replace("GET STARTED", "SEARCH"))
        self.btn_load_more.setText("Load More")
        self.btn_download.setText("DOWNLOAD TO LIBRARY")
        
        # 3. Search
        self.search_input.setPlaceholderText("Search...")
        
        # 4. Inspector
        self.lbl_inspector_header.setText("METADATA")

    def apply_theme(self, t):
        self.setStyleSheet(f"background-color: {t.get('bg_main')}; color: {t.get('text_main')};")
        
        # Tabs
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: none; }}
            QTabBar::tab {{
                background: {t.get('bg_toolbar')};
                color: {t.get('text_secondary')};
                padding: 8px 20px;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {t.get('accent')};
                border-bottom: 2px solid {t.get('accent')};
                background: {t.get('bg_secondary')};
                font-weight: bold;
            }}
        """)
        
        # Toolbars & Headers
        header_style = f"background-color: {t.get('bg_secondary')}; border-bottom: 1px solid {t.get('border')};"
        if hasattr(self, 'local_toolbar'): self.local_toolbar.setStyleSheet(header_style)
        if hasattr(self, 'search_bar'): self.search_bar.setStyleSheet(header_style)
        if hasattr(self, 'video_player'): self.video_player.apply_theme(t)
        
        # Inspector child stylesheet for dynamic labels
        if hasattr(self, 'inspector'):
            self.inspector.setStyleSheet(f"""
                QWidget#inspector {{ 
                    background-color: {t.get('bg_secondary')}; 
                    border-left: 1px solid {t.get('border')}; 
                }}
                QLabel {{ 
                    color: {t.get('text_main')}; 
                    font-size: 12px; 
                    border: none; 
                    background: transparent;
                }}
            """)
        
        # Grids
        self.video_grid.setStyleSheet(self._grid_style(t))
        self.online_grid.setStyleSheet(self._grid_style(t))
        
        # Header Label (Specific override)
        if hasattr(self, 'lbl_inspector_header'):
            self.lbl_inspector_header.setStyleSheet(f"color: {t.get('text_secondary')}; font-size: 11px; font-weight: bold; margin-bottom: 5px; background: transparent;")
            
        # Inputs & More Buttons
        self.search_input.setStyleSheet(f"background-color: {t.get('bg_button')}; color: {t.get('text_main')}; border: 1px solid {t.get('border')}; padding: 8px; border-radius: 4px;")
        self.btn_load_more.setStyleSheet(f"""
            QPushButton {{
                background-color: {t.get('bg_button')};
                color: {t.get('text_secondary')};
                border: 1px solid {t.get('border')};
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
                margin-top: 10px;
            }}
            QPushButton:hover {{
                background-color: {t.get('bg_button_hover')};
                color: {t.get('text_main')};
            }}
        """)
