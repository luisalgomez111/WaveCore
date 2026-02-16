from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
                              QListWidget, QListWidgetItem, QLabel, QPushButton, QFileDialog, 
                              QTabWidget, QLineEdit, QApplication, QMessageBox, QFrame, QScrollArea, QButtonGroup, QMenu, QInputDialog)
from PyQt6.QtGui import QPixmap, QImage, QIcon, QDrag
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QUrl, QMimeData, QPoint
from utils.pixabay_client import PixabayClient
from utils.pexels_client import PexelsClient
from utils.unsplash_client import UnsplashClient
import utils.file_ops as fops
import requests
import os


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

class DraggablePhotoListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item: return
        
        path = item.data(Qt.ItemDataRole.UserRole)
        # Only drag local files
        if not path or not isinstance(path, str) or not os.path.exists(path): return
        
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(path)])
        drag.setMimeData(mime_data)
        
        pixmap = item.icon().pixmap(200, 200)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
        
        drag.exec(Qt.DropAction.CopyAction)

class PhotoPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.localizer = main_window.localizer
        self.pixabay = PixabayClient()
        self.pexels = PexelsClient()
        self.unsplash = UnsplashClient()
        self.loader_threads = []
        self.current_page = 1
        self.current_query = ""
        self.init_ui()
        self.load_library()
        
    def load_library(self):
        fops.ensure_vault_exists()
        photo_path = fops.get_photo_path()
        if os.path.exists(photo_path):
            with os.scandir(photo_path) as it:
                for entry in it:
                     if entry.is_file():
                        ext = os.path.splitext(entry.name)[1].lower()
                        if ext in ('.jpg', '.jpeg', '.png', '.webp', '.bmp'):
                            self.add_photo_to_grid(entry.path)
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Splitter: Tabs (Left) / Inspector (Right)
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
        
        # TAB 1: LOCAL GALLERY
        tab_local = QWidget()
        local_layout = QVBoxLayout(tab_local)
        local_layout.setContentsMargins(0, 0, 0, 0)
        
        local_toolbar = QWidget()
        local_toolbar.setObjectName("toolbar")
        local_toolbar.setFixedHeight(40)
        local_toolbar.setStyleSheet("background-color: #1f1f1f; border-bottom: 1px solid #333;")
        self.local_toolbar = local_toolbar
        lt_layout = QHBoxLayout(local_toolbar)
        
        self.btn_import = QPushButton("Import Photos")
        self.btn_import.setStyleSheet("background-color: #333; color: white; border: none; padding: 5px 10px;")
        self.btn_import.clicked.connect(self.import_photos)
        lt_layout.addWidget(self.btn_import)
        lt_layout.addStretch()
        local_layout.addWidget(local_toolbar)
        
        self.photo_grid = DraggablePhotoListWidget()
        self.photo_grid.setViewMode(QListWidget.ViewMode.IconMode)
        self.photo_grid.setIconSize(QSize(180, 180))
        self.photo_grid.setGridSize(QSize(200, 240))
        self.photo_grid.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.photo_grid.setSpacing(10)
        self.photo_grid.setWordWrap(True)
        self.photo_grid.setStyleSheet(self._grid_style())
        self.photo_grid.itemClicked.connect(self.on_photo_selected)
        self.photo_grid.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.photo_grid.customContextMenuRequested.connect(self.open_photo_menu)
        local_layout.addWidget(self.photo_grid)
        
        self.tabs.addTab(tab_local, "Local Gallery")
        
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
        
        self.btn_unsplash = QPushButton("Unsplash")
        self.btn_unsplash.setCheckable(True)
        self.btn_unsplash.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_unsplash.setFixedHeight(30)

        self.source_group.addButton(self.btn_pixabay)
        self.source_group.addButton(self.btn_pexels)
        self.source_group.addButton(self.btn_unsplash)
        self.source_group.buttonClicked.connect(self.on_provider_changed)
        
        # Style for toggles
        toggle_style = """
            QPushButton {
                background-color: #333;
                color: #888;
                border: none;
                padding: 5px 10px;
                font-weight: bold;
                border-radius: 4px;
                font-size: 11px;
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
        self.btn_unsplash.setStyleSheet(toggle_style)
        
        sb_layout.addWidget(self.btn_pixabay)
        sb_layout.addWidget(self.btn_pexels)
        sb_layout.addWidget(self.btn_unsplash)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Photos...")
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
        self.online_grid.setIconSize(QSize(180, 180))
        self.online_grid.setGridSize(QSize(200, 240))
        self.online_grid.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.online_grid.setSpacing(10)
        self.online_grid.setWordWrap(True)
        self.online_grid.setStyleSheet(self._grid_style())
        self.online_grid.itemClicked.connect(self.on_online_photo_selected)
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
        
        # Preview Area
        self.preview_lbl = QLabel()
        self.preview_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_lbl.setMinimumHeight(400)
        self.preview_lbl.setStyleSheet("background-color: #121212; border-bottom: 1px solid #333;")
        ins_layout.addWidget(self.preview_lbl)
        
        # Metadata Scrollable area
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
        
        # Metadata Labels
        self.lbl_name = self._create_meta_label("Name: -")
        self.lbl_res = self._create_meta_label("Resolution: -")
        self.lbl_size = self._create_meta_label("Size: -")
        self.lbl_format = self._create_meta_label("Format: -")
        self.lbl_path = self._create_meta_label("Path: -")
        self.lbl_path.setWordWrap(True)
        
        for l in [self.lbl_name, self.lbl_res, self.lbl_size, self.lbl_format, self.lbl_path]:
            meta_layout.addWidget(l)

        # Download Button (Initially Hidden)
        self.btn_download = QPushButton("DOWNLOAD TO LIBRARY")
        self.btn_download.setStyleSheet("background-color: #D75239; color: white; padding: 10px; border-radius: 4px; font-weight: bold; margin-top: 10px;")
        self.btn_download.setVisible(False)
        self.btn_download.clicked.connect(self.download_current_photo)
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
                QListWidget { background-color: #121212; border: none; padding: 15px; }
                QListWidget::item { background-color: #1a1a1a; border-radius: 8px; color: #ddd; }
                QListWidget::item:selected { background-color: #D75239; color: white; border: 2px solid #D75239; }
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
                border-radius: 8px;
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
        # Style will be handled by apply_theme or parent stylesheet
        return lbl

    def import_photos(self):
        title = self.main_window.localizer.get("menu_import")
        files, _ = QFileDialog.getOpenFileNames(self, title, "", "Images (*.jpg *.png *.webp *.bmp)")
        if files:
            for f in files:
                self.add_photo_to_grid(f)

    def add_photo_to_grid(self, path):
        name = os.path.basename(path)
        item = QListWidgetItem(name)
        item.setData(Qt.ItemDataRole.UserRole, path)
        
        pix = QPixmap(path)
        if not pix.isNull():
            icon = QIcon(pix.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
            item.setIcon(icon)
            
        self.photo_grid.addItem(item)

    # --- FILE MANAGEMENT ---
    def open_photo_menu(self, position):
        selected_items = self.photo_grid.selectedItems()
        if not selected_items: return
        
        menu = QMenu()
        if len(selected_items) == 1:
            action_rename = menu.addAction(self.main_window.localizer.get("ctx_rename_file").replace(" File", ""))
            action_rename.triggered.connect(lambda: self.rename_selected_photo(selected_items[0]))
            
        action_delete = menu.addAction(self.main_window.localizer.get("ctx_delete_file").format(len(selected_items)))
        action_delete.triggered.connect(self.delete_selected_photos)
        
        menu.exec(self.photo_grid.viewport().mapToGlobal(position))

    def rename_selected_photo(self, item):
        old_path = item.data(Qt.ItemDataRole.UserRole)
        if not old_path or not os.path.exists(old_path): return
        
        old_name = os.path.basename(old_path)
        title = self.main_window.localizer.get("msg_rename")
        label = self.main_window.localizer.get("msg_new_name")
        text, ok = QInputDialog.getText(self, title, label, text=old_name)
        if ok and text and text != old_name:
            try:
                new_path = fops.rename_item(old_path, text)
                item.setData(Qt.ItemDataRole.UserRole, new_path)
                item.setText(text)
                # Refresh inspector if this was the visible one
                self.on_photo_selected(item)
            except Exception as e:
                QMessageBox.critical(self, self.main_window.localizer.get("msg_error"), str(e))

    def delete_selected_photos(self):
        items = self.photo_grid.selectedItems()
        if not items: return
        
        msg = self.main_window.localizer.get("msg_confirm_delete_multi").format(len(items))
        reply = QMessageBox.question(self, self.main_window.localizer.get("ctx_delete"), 
                                     msg,
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            for item in items:
                path = item.data(Qt.ItemDataRole.UserRole)
                if path and os.path.exists(path):
                    try:
                        fops.delete_item(path)
                        self.photo_grid.takeItem(self.photo_grid.row(item))
                    except Exception as e:
                        print(f"Error deleting {path}: {e}")
            self.lbl_name.setText("Author: -")
            self.preview_lbl.clear()

    def on_photo_selected(self, item):
        selected_count = len(self.photo_grid.selectedItems())
        if selected_count > 1:
            self.preview_lbl.setText(f"{selected_count} {self.localizer.get('module_photo')}s Selected")
            self.lbl_name.setText(f"{self.localizer.get('msg_selection') if self.localizer.get('msg_selection') != 'msg_selection' else 'Selection'}: {selected_count}")
            self.lbl_res.setText("-")
            self.lbl_size.setText("-")
            self.lbl_format.setText("-")
            self.lbl_path.setText("-")
            self.btn_download.setVisible(False)
            return

        path = item.data(Qt.ItemDataRole.UserRole)
        self.btn_download.setVisible(False) 
        if path and os.path.exists(path):
            self.update_inspector(path, is_online=False)

    def update_inspector(self, data, is_online=False):
        if not is_online:
            path = data
            pix = QPixmap(path)
            if not pix.isNull():
                scaled = pix.scaled(self.preview_lbl.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.preview_lbl.setPixmap(scaled)
                
                self.lbl_name.setText(f"Name: {os.path.basename(path)}")
                self.lbl_res.setText(f"Resolution: {pix.width()} x {pix.height()}")
                self.lbl_size.setText(f"Size: {os.path.getsize(path) / 1024:.1f} KB")
                self.lbl_format.setText(f"Format: {os.path.splitext(path)[1].upper()}")
                self.lbl_path.setText(f"Path: {path}")
        else:
            hit = data
            source = hit.get('_source', 'Pixabay')
            
            if source == 'Pixabay':
                url = hit.get("largeImageURL") or hit.get("webformatURL")
                preview_url = hit.get("previewURL")
                
                self.lbl_name.setText(f"User: {hit.get('user')}")
                self.lbl_res.setText(f"Resolution: {hit.get('imageWidth')} x {hit.get('imageHeight')}")
                self.lbl_size.setText(f"Size: {hit.get('imageSize') / 1024:.1f} KB")
                self.lbl_format.setText("Format: JPG")
                self.lbl_path.setText(f"Source: Pixabay")
            
            elif source == 'Pexels':
                src = hit.get("src", {})
                url = src.get("original")
                preview_url = src.get("medium")
                
                self.lbl_name.setText(f"Photographer: {hit.get('photographer')}")
                self.lbl_res.setText(f"Resolution: {hit.get('width')} x {hit.get('height')}")
                self.lbl_size.setText("Size: -")
                self.lbl_format.setText("Format: JPG")
                self.lbl_path.setText(f"Source: Pexels")
            
            else: # Unsplash
                url = hit.get("urls", {}).get("full")
                preview_url = hit.get("urls", {}).get("small")
                user = hit.get("user", {})
                
                self.lbl_name.setText(f"User: {user.get('name') or user.get('username')}")
                self.lbl_res.setText(f"Resolution: {hit.get('width')} x {hit.get('height')}")
                self.lbl_size.setText("Size: -")
                self.lbl_format.setText("Format: JPG")
                self.lbl_path.setText("Source: Unsplash")

            # Load preview image implementation 
            try:
                # Use a cached/session or just simple get. 
                # Ideally we use an async loader for the preview too but let's keep it simple for now as it's small.
                data_resp = requests.get(preview_url, timeout=5).content
                pix = QPixmap()
                pix.loadFromData(data_resp)
                scaled = pix.scaled(self.preview_lbl.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.preview_lbl.setPixmap(scaled)
            except:
                pass

            self.current_download_url = url
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
        elif self.btn_pexels.isChecked(): source = "Pexels"
        else: source = "Unsplash"

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
                results = self.pixabay.search_images(self.current_query, page=self.current_page)
            elif source == "Pexels":
                results = self.pexels.search_photos(self.current_query, page=self.current_page)
            else: # Unsplash
                results = self.unsplash.search_photos(self.current_query, page=self.current_page)
                
            if not results and self.current_page == 1:
                self.online_grid.addItem(self.localizer.get("msg_no_results"))
            elif results:
                self.btn_load_more.setVisible(True)
                
            for hit in results:
                item = QListWidgetItem()
                thumb_url = ""
                
                if source == "Pixabay":
                      item.setText(f"ID: {hit.get('id')}")
                      thumb_url = hit.get("previewURL")
                elif source == "Pexels":
                      item.setText(f"ID: {hit.get('id')}")
                      src = hit.get("src", {})
                      thumb_url = src.get("medium") or src.get("small")
                else: # Unsplash
                      item.setText(f"ID: {hit.get('id')}")
                      urls = hit.get("urls", {})
                      thumb_url = urls.get("small") or urls.get("thumb")

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
            if self.current_page == 1: 
                self.online_grid.addItem(self.main_window.localizer.get("msg_search_error"))
        finally:
            QApplication.restoreOverrideCursor()

    def on_thumbnail_loaded(self, item, pixmap):
        scaled = pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        item.setIcon(QIcon(scaled))
        item.setText("")

    def on_online_photo_selected(self, item):
        hit = item.data(Qt.ItemDataRole.UserRole)
        if hit:
            self.update_inspector(hit, is_online=True)

    def download_current_photo(self):
        if not hasattr(self, 'current_download_url') or not self.current_download_url:
            return

        vault_path = fops.get_photo_path()
        filename = os.path.basename(self.current_download_url).split("?")[0]
        save_path = os.path.join(vault_path, filename)

        msg = self.localizer.get("msg_download_confirm").format(save_path)
        reply = QMessageBox.question(self, self.localizer.get("ctx_download") if self.localizer.get("ctx_download") != "ctx_download" else "Download", msg, 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:
                success = False
                
                # Try to get source from current item if selected
                current_source = "Pixabay"
                if self.online_grid.currentItem():
                    hit = self.online_grid.currentItem().data(Qt.ItemDataRole.UserRole)
                    current_source = hit.get('_source', 'Pixabay')

                if current_source == "Pexels":
                     success = self.pexels.download_file(self.current_download_url, save_path)
                elif current_source == "Unsplash":
                     success = self.unsplash.download_file(self.current_download_url, save_path)
                else:
                     success = self.pixabay.download_file(self.current_download_url, save_path)
                     
                if success:
                    QMessageBox.information(self, self.localizer.get("msg_success"), self.localizer.get("msg_download_success"))
                    self.add_photo_to_grid(save_path)
                else:
                    QMessageBox.warning(self, self.localizer.get("msg_error"), self.localizer.get("msg_download_failed"))
            finally:
                QApplication.restoreOverrideCursor()
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
        self.photo_grid.setStyleSheet(self._grid_style(t))
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
