from utils.constants import VERSION

TRANSLATIONS = {
    "en": {
        "window_title": f"WaveCore Audio Library v{VERSION}",
        "library_header": "    WAVECORE VAULT",
        "menu_file": "File",
        "menu_import": "Import Folder...",
        "menu_exit": "Exit",
        "menu_language": "Language",
        "menu_help": "Help",
        "menu_about": "About",
        "menu_creator": "Creator & License",
        "dialog_about_title": "About WaveCore",
        "dialog_about_text": f"WaveCore v{VERSION}",
        "dialog_about_html": f"""
            <h2 style='color: #D75239;'>WaveCore Audio Library</h2>
            <p><b>Version {VERSION}</b> | Professional Build 2026</p>
            <p>WaveCore is a top-tier media management solution designed for world-class sound designers and video editors. It offers a seamless bridge between your asset library and your professional creative workflow.</p>
            <h3>Core Technical Capabilities:</h3>
            <ul style='margin-left: 15px;'>
                <li><b>High-Performance Management:</b> Blazing-fast organization for Audio, Video, and Photo assets in a unified interface.</li>
                <li><b>Interactive Waveform Engine:</b> Real-time waveform generation with precise scrubbing and instant Drag & Drop export to any professional DAW.</li>
                <li><b>Smart Batch Operations:</b> Pro-grade multi-selection for powerful bulk deletion, renaming, and asset categorization.</li>
                <li><b>Modern Architectural Design:</b> Minimalist, high-performance UI inspired by DaVinci Resolve and optimized for productivity.</li>
            </ul>
        """,
        "dialog_creator_title": "Creator & License",
        "dialog_creator_text": "Created by Luis Alberto Gómez",
        "dialog_creator_info": "Lead Developer: Luis Alberto Gómez\n\n© 2026 Luis Alberto Gómez. All rights reserved.",
        "dialog_select_folder": "Select Audio Folder",
        "status_loading": "Loading: {}",
        "status_loaded": "Loaded {} tracks.",
        "ctx_new_folder": "New Folder",
        "ctx_rename": "Rename Folder",
        "ctx_delete": "Delete Folder",
        "ctx_rename_file": "Rename File",
        "ctx_delete_file": "Delete Selected ({})",
        "menu_updates": "Check for Updates",
        "status_no_updates": "You already have the latest version.",
        "status_update_available": "Update Available",
        "status_update_msg": "A new version of WaveCore is available! ({})\n\nDownload now?",
        "col_name": "Name",
        "col_channels": "Channels",
        "col_format": "Format",
        "col_duration": "Duration",
        "col_genre": "Genre",
        "col_bpm": "BPM",
        "col_waveform": "Waveform",
        "btn_welcome_start": "GET STARTED",
        "btn_visit_web": "WEBSITE",
        "dialog_welcome_title": "Welcome to WaveCore",
        "welcome_header": "Elevate Your Creative Workflow",
        "welcome_sub": "The ultimate local vault for professional assets. Powered by speed, designed for clarity.",
        "welcome_support_title": "SUPPORT WAVECORE",
        "welcome_support_desc": "Help us develop new features by supporting the project.",
        "welcome_copy_success": "ADDRESS COPIED!",
        "module_audio_desc": "Waveform scrubbing and precise export.",
        "module_video_desc": "Smooth playback and cinematic indexing.",
        "module_photo_desc": "HD metadata vault and gallery view.",
        "dialog_welcome_html": """
            <div style='margin-bottom: 20px;'>
                <h2 style='color: #D75239; margin-bottom: 5px;'>WaveCore v2.0 Professional</h2>
                <p style='color: #888; font-size: 13px;'>The most powerful media vault for creative workflows.</p>
            </div>
            <!-- HEADER_END -->
            <div style='display: flex; gap: 15px;'>
                <div class='module-card'>
                    <h3 style='color: #D75239; font-size: 15px; margin-bottom: 5px;'>🔊 AUDIO ENGINE</h3>
                    <p style='font-size: 12px;'>Interactive waveform with precision scrubbing and instant DAW export.</p>
                </div>
                <div class='module-card'>
                    <h3 style='color: #D75239; font-size: 15px; margin-bottom: 5px;'>🎬 VIDEO PREVIEW</h3>
                    <p style='font-size: 12px;'>Fast indexing and smooth playback for your video asset library.</p>
                </div>
                <div class='module-card'>
                    <h3 style='color: #D75239; font-size: 15px; margin-bottom: 5px;'>🖼️ PHOTO VAULT</h3>
                    <p style='font-size: 12px;'>Optimized gallery for managing photos with high-resolution previews.</p>
                </div>
            </div>
            <!-- SHOWCASE_END -->
            <ul id='module_captions' style='display:none;'>
                <li>Audio: Pro waveform & DAW export</li>
                <li>Video: Smooth cinematic playback</li>
                <li>Photo: HD gallery & metadata</li>
            </ul>
            <div style='margin-top: 20px; padding: 10px; background: #222; border-radius: 5px;'>
                <p style='font-size: 12px;'><b style='color: #ff6d50;'>WHAT'S NEW:</b> Pro multi-selection, enhanced media inspectors, and a unified performance engine.</p>
            </div>
            <div style='margin-top: 15px; border-top: 1px solid #333; padding-top: 10px;'>
                <p style='font-size: 12px;'>🌐 <a href='https://wave-core.vercel.app/' style='color: #D75239; text-decoration: none;'>Official Website</a> | <a href='https://github.com/luisalgomez111/WaveCore' style='color: #D75239; text-decoration: none;'>GitHub</a> | <b>WaveCore Project 2026</b></p>
            </div>
        """,
        "msg_error": "Error",
        "msg_success": "Success",
        "msg_rename": "Rename",
        "msg_new_name": "New Name:",
        "msg_confirm_delete": "Are you sure you want to delete '{}' and all its contents?",
        "msg_import_first": "Please import a library folder first.",
        "msg_invalid_folder": "Selected item is not a valid folder.",
        "msg_playback_error": "Playback Error",
        "module_audio": "AUDIO",
        "module_video": "VIDEO",
        "module_photo": "PHOTO",
        "msg_confirm_delete_multi": "Are you sure you want to delete {} items permanently?",
        "msg_download_confirm": "Download to:\n{}?",
        "msg_download_success": "Download complete!",
        "msg_download_failed": "Download failed.",
        "msg_no_results": "No results found.",
        "msg_search_error": "Error searching.",
    },
    "es": {
        "window_title": f"Librería WaveCore v{VERSION}",
        "library_header": "    BÓVEDA WAVECORE",
        "menu_file": "Archivo",
        "menu_import": "Importar Carpeta...",
        "menu_exit": "Salir",
        "menu_language": "Idioma",
        "menu_help": "Ayuda",
        "menu_about": "Acerca de",
        "menu_creator": "Creador y Licencia",
        "dialog_about_title": "Acerca de WaveCore",
        "dialog_about_text": f"WaveCore v{VERSION}",
        "dialog_about_html": f"""
            <h2 style='color: #D75239;'>Librería de Audio WaveCore</h2>
            <p><b>Versión {VERSION}</b> | Build Profesional 2026</p>
            <p>WaveCore es la solución de élite diseñada para diseñadores de sonido y editores que exigen la máxima eficiencia en la gestión de activos multimedia.</p>
            <h3>Capacidades Técnicas de Vanguardia:</h3>
            <ul style='margin-left: 15px;'>
                <li><b>Gestión Global de Activos:</b> Organización profesional de Audio, Video y Fotos bajo una interfaz unificada y ultra-rápida.</li>
                <li><b>Motor de Onda Interactiva:</b> Visualización de alta fidelidad con Scrubbing y exportación inmediata mediante Drag & Drop a cualquier DAW.</li>
                <li><b>Operaciones por Lote Inteligentes:</b> Selección múltiple de grado profesional para borrar, renombrar y categorizar activos masivamente.</li>
                <li><b>Diseño Arquitectónico Moderno:</b> Interfaz minimalista inspirada en flujos de trabajo profesionales como DaVinci Resolve.</li>
            </ul>
        """,
        "dialog_creator_title": "Creador y Licencia",
        "dialog_creator_text": "Creado por Luis Alberto Gómez",
        "dialog_creator_info": "Desarrollador Principal: Luis Alberto Gómez\n\n© 2026 Luis Alberto Gómez. Todos los derechos reservados.",
        "dialog_select_folder": "Seleccionar Carpeta",
        "status_loading": "Cargando: {}",
        "status_loaded": "Se cargaron {} archivos.",
        "ctx_new_folder": "Nueva Carpeta",
        "ctx_rename": "Renombrar Carpeta",
        "ctx_delete": "Eliminar Carpeta",
        "ctx_rename_file": "Renombrar Archivo",
        "ctx_delete_file": "Eliminar Seleccionados ({})",
        "menu_updates": "Actualizaciones",
        "status_no_updates": "Ya tienes la última versión.",
        "status_update_available": "Actualización Disponible",
        "status_update_msg": "¡Hay una nueva versión ({})!\n\n¿Quieres descargarla ahora?",
        "col_name": "Nombre",
        "col_channels": "Canales",
        "col_format": "Formato",
        "col_duration": "Duración",
        "col_genre": "Género",
        "col_bpm": "BPM",
        "col_waveform": "Onda",
        "btn_welcome_start": "COMENZAR",
        "btn_visit_web": "PÁGINA WEB",
        "dialog_welcome_title": "Bienvenido a WaveCore",
        "welcome_header": "Eleva tu Flujo Creativo",
        "welcome_sub": "La bóveda local definitiva para activos profesionales. Potencia y claridad.",
        "welcome_support_title": "APOYA A WAVECORE",
        "welcome_support_desc": "Ayúdanos a desarrollar nuevas funciones apoyando el proyecto.",
        "welcome_copy_success": "¡DIRECCIÓN COPIADA!",
        "module_audio_desc": "Scrubbing de onda y exportación precisa.",
        "module_video_desc": "Reproducción fluida e indexación de cine.",
        "module_photo_desc": "Bóveda HD y vista de galería pro.",
        "dialog_welcome_html": """
            <div style='margin-bottom: 20px;'>
                <h2 style='color: #D75239; margin-bottom: 5px;'>WaveCore v2.0 Profesional</h2>
                <p style='color: #888; font-size: 13px;'>La bóveda de medios más potente para flujos creativos.</p>
            </div>
            <!-- HEADER_END -->
            <div style='display: flex; gap: 15px;'>
                <div class='module-card'>
                    <h3 style='color: #D75239; font-size: 15px; margin-bottom: 5px;'>🔊 MOTOR DE AUDIO</h3>
                    <p style='font-size: 12px;'>Onda interactiva con scrubbing de precisión y exportación instantánea a DAW.</p>
                </div>
                <div class='module-card'>
                    <h3 style='color: #D75239; font-size: 15px; margin-bottom: 5px;'>🎬 PREVIEW DE VIDEO</h3>
                    <p style='font-size: 12px;'>Indexación rápida y reproducción fluida para tu librería de videos.</p>
                </div>
                <div class='module-card'>
                    <h3 style='color: #D75239; font-size: 15px; margin-bottom: 5px;'>🖼️ BÓVEDA DE FOTOS</h3>
                    <p style='font-size: 12px;'>Galería optimizada para gestionar fotos con previsualización en alta resolución.</p>
                </div>
            </div>
            <!-- SHOWCASE_END -->
            <ul id='module_captions' style='display:none;'>
                <li>Audio: Onda pro y exportación a DAW</li>
                <li>Video: Reproducción cinematográfica</li>
                <li>Photo: Galería HD y metadatos</li>
            </ul>
            <div style='margin-top: 20px; padding: 10px; background: #222; border-radius: 5px;'>
                <p style='font-size: 12px;'><b style='color: #ff6d50;'>NOVEDADES:</b> Multi-selección Pro, inspectores de medios mejorados y un motor de rendimiento unificado.</p>
            </div>
            <div style='margin-top: 15px; border-top: 1px solid #333; padding-top: 10px;'>
                <p style='font-size: 12px;'>🌐 <a href='https://wave-core.vercel.app/' style='color: #D75239; text-decoration: none;'>Sitio Web Oficial</a> | <a href='https://github.com/luisalgomez111/WaveCore' style='color: #D75239; text-decoration: none;'>GitHub</a> | <b>WaveCore Project 2026</b></p>
            </div>
        """,
        "msg_error": "Error",
        "msg_success": "Éxito",
        "msg_rename": "Renombrar",
        "msg_new_name": "Nuevo Nombre:",
        "msg_confirm_delete": "¿Estás seguro de que quieres eliminar '{}' y todo su contenido?",
        "msg_import_first": "Por favor, importa una carpeta de librería primero.",
        "msg_invalid_folder": "El elemento seleccionado no es una carpeta válida.",
        "msg_playback_error": "Error de Reproducción",
        "module_audio": "AUDIO",
        "module_video": "VIDEO",
        "module_photo": "FOTO",
        "msg_confirm_delete_multi": "¿Estás seguro de que quieres eliminar {} elementos permanentemente?",
        "msg_download_confirm": "¿Descargar en:\n{}?",
        "msg_download_success": "¡Descarga completada!",
        "msg_download_failed": "La descarga falló.",
        "msg_no_results": "No se encontraron resultados.",
        "msg_search_error": "Error en la búsqueda.",
    },
    "ru": {
        "window_title": f"WaveCore Audio Library v{VERSION}",
        "library_header": "    БИБЛИОТЕКА WAVECORE",
        "menu_file": "Файл",
        "menu_import": "Импорт папки...",
        "menu_exit": "Выход",
        "menu_language": "Язык",
        "menu_help": "Справка",
        "menu_about": "О программе",
        "menu_creator": "Автор и Лицензия",
        "dialog_about_title": "О WaveCore",
        "dialog_about_html": f"""
            <h2 style='color: #D75239;'>WaveCore Audio Library</h2>
            <p><b>Версия {VERSION}</b></p>
            <p>WaveCore — это комплексное решение для саунд-дизайнеров и редакторов.</p>
            <h3>Основные возможности:</h3>
            <ul>
                <li><b>Управление медиа:</b> Организация аудио, видео и фото.</li>
                <li><b>Интерактивная волна:</b> Предпросмотр, скраббинг и экспорт Drag & Drop в DAW.</li>
                <li><b>Умное управление:</b> Массовое удаление и переименование.</li>
            </ul>
        """,
        "dialog_creator_title": "Автор и Лицензия",
        "dialog_creator_text": "Автор: Luis Alberto Gómez",
        "dialog_creator_info": "Ведущий разработчик: Luis Alberto Gómez\n\n© 2026. Все права защищены.",
        "dialog_select_folder": "Выбрать папку",
        "status_loading": "Загрузка: {}",
        "status_loaded": "Загружено {} файлов.",
        "ctx_new_folder": "Новая папка",
        "ctx_rename": "Переименовать папку",
        "ctx_delete": "Удалить папку",
        "ctx_rename_file": "Переименовать файл",
        "ctx_delete_file": "Удалить выбранные ({})",
        "menu_updates": "Обновления",
        "btn_welcome_start": "НАЧАТЬ",
        "dialog_welcome_title": "Добро пожаловать в WaveCore",
        "dialog_welcome_html": """
            <h2 style='color: #D75239;'>Добро пожаловать!</h2>
            <p>Ваш набор инструментов для медиа. Что нового:</p>
            <ul style='margin-left: 15px;'>
                <li><b>Минималистичный дизайн:</b> Обновленная панель воспроизведения.</li>
                <li><b>Мультивыбор:</b> Работайте с несколькими файлами одновременно.</li>
            </ul>
        """,
        "msg_error": "Ошибка",
        "msg_success": "Успех",
        "msg_rename": "Переименовать",
        "msg_new_name": "Новое имя:",
        "msg_confirm_delete": "Вы уверены, что хотите удалить '{}' и все его содержимое?",
        "msg_import_first": "Сначала импортируйте папку библиотеки.",
        "msg_invalid_folder": "Выбранный элемент не является папкой.",
        "msg_playback_error": "Ошибка воспроизведения",
        "module_audio": "АУДИО",
        "module_video": "ВИДЕО",
        "module_photo": "ФОТО",
    },
    "zh": {
        "window_title": f"WaveCore 音频库 v{VERSION}",
        "library_header": "    WAVECORE 库",
        "menu_file": "文件",
        "menu_import": "导入文件夹...",
        "menu_exit": "退出",
        "menu_language": "语言",
        "menu_help": "帮助",
        "menu_about": "关于",
        "menu_creator": "创作者与许可",
        "dialog_about_title": "关于 WaveCore",
        "dialog_about_html": f"""
            <h2 style='color: #D75239;'>WaveCore 音频库</h2>
            <p><b>版本 {VERSION}</b></p>
            <p>WaveCore 是为声音设计师和编辑设计的综合资产管理解决方案。</p>
            <h3>核心功能：</h3>
            <ul>
                <li><b>媒体管理：</b> 高效整理音频、视频和照片。</li>
                <li><b>交互式波形：</b> 支持擦除预览及快速拖动导出至 DAW。</li>
                <li><b>智能管理：</b> 支持多选批量删除和重命名。</li>
            </ul>
        """,
        "dialog_creator_title": "创作者与许可",
        "dialog_creator_text": "创作者：Luis Alberto Gómez",
        "dialog_creator_info": "首席开发人员：Luis Alberto Gómez\n\n© 2026 Luis Alberto Gómez. 保留所有权利。",
        "dialog_select_folder": "选择文件夹",
        "status_loading": "正在加载：{}",
        "status_loaded": "已加载 {} 个文件。",
        "ctx_new_folder": "新建文件夹",
        "ctx_rename": "重命名文件夹",
        "ctx_delete": "删除文件夹",
        "ctx_rename_file": "重命名文件",
        "ctx_delete_file": "删除所选 ({})",
        "menu_updates": "检查更新",
        "btn_welcome_start": "开始使用",
        "dialog_welcome_title": "欢迎使用 WaveCore",
        "dialog_welcome_html": """
            <h2 style='color: #D75239;'>欢迎使用 WaveCore!</h2>
            <p>您的媒体管理工具包。新功能：</p>
            <ul style='margin-left: 15px;'>
                <li><b>统一设计：</b> 极简主义外观与重新设计的播放栏。</li>
                <li><b>多选功能：</b> 批量管理照片和视频。</li>
            </ul>
        """,
        "msg_error": "错误",
        "msg_success": "成功",
        "msg_rename": "重命名",
        "msg_new_name": "新名称：",
        "msg_confirm_delete": "您确定要删除“{}”及其所有内容吗？",
        "msg_import_first": "请先导入库文件夹。",
        "msg_invalid_folder": "所选项目不是有效的文件夹。",
        "msg_playback_error": "播放错误",
        "module_audio": "音频",
        "module_video": "视频",
        "module_photo": "照片",
    },
    "fr": {
        "window_title": f"WaveCore Audio v{VERSION}",
        "library_header": "    COFFRE WAVECORE",
        "menu_file": "Fichier",
        "menu_import": "Importer le dossier...",
        "menu_exit": "Quitter",
        "menu_language": "Langue",
        "menu_help": "Aide",
        "menu_about": "À propos",
        "menu_creator": "Créateur & Licence",
        "dialog_about_title": "À propos de WaveCore",
        "dialog_about_html": f"""
            <h2 style='color: #D75239;'>WaveCore Audio Library</h2>
            <p><b>Version {VERSION}</b></p>
            <p>Solution complète pour les designers sonores et monteurs.</p>
            <h3>Capacités :</h3>
            <ul>
                <li><b>Gestion des médias :</b> Organisation audio, vidéo et photo.</li>
                <li><b>Forme d'onde :</b> Scrubbing et export Drag & Drop vers DAW.</li>
                <li><b>Gestion Intelligente :</b> Sélection multiple et édition par lot.</li>
            </ul>
        """,
        "dialog_creator_title": "Créateur & Licence",
        "dialog_creator_text": "Créé par Luis Alberto Gómez",
        "dialog_creator_info": "Développeur Principal: Luis Alberto Gómez\n\n© 2026. Tous droits réservés.",
        "dialog_select_folder": "Sélectionner le dossier",
        "status_loading": "Chargement : {}",
        "status_loaded": "{} fichiers chargés.",
        "ctx_new_folder": "Nouveau dossier",
        "ctx_rename": "Renommer le dossier",
        "ctx_delete": "Supprimer le dossier",
        "ctx_rename_file": "Renommer le fichier",
        "ctx_delete_file": "Supprimer la sélection ({})",
        "menu_updates": "Mises à jour",
        "btn_welcome_start": "COMMENCER",
        "dialog_welcome_title": "Bienvenue sur WaveCore",
        "dialog_welcome_html": """
            <h2 style='color: #D75239;'>Bienvenue sur WaveCore !</h2>
            <p>Votre boîte à outils multimédia. Nouveautés :</p>
            <ul style='margin-left: 15px;'>
                <li><b>Design Épuré :</b> Look minimaliste et barre de lecture intégrée.</li>
                <li><b>Multi-sélection :</b> Gérez plusieurs fichiers à la fois.</li>
            </ul>
        """,
        "msg_error": "Erreur",
        "msg_success": "Succès",
        "msg_rename": "Renommer",
        "msg_new_name": "Nouveau nom :",
        "msg_confirm_delete": "Êtes-vous sûr de vouloir supprimer '{}' et tout son contenu ?",
        "msg_import_first": "Veuillez d'abord importer un dossier de bibliothèque.",
        "msg_invalid_folder": "L'élément sélectionné n'est pas un dossier valide.",
        "msg_playback_error": "Erreur de lecture",
        "module_audio": "AUDIO",
        "module_video": "VIDÉO",
        "module_photo": "PHOTO",
    }
}

class Localizer:
    def __init__(self, lang="es"):
        self.lang = lang

    def set_language(self, lang):
        if lang in TRANSLATIONS:
            self.lang = lang

    def get(self, key):
        return TRANSLATIONS.get(self.lang, TRANSLATIONS["en"]).get(key, key)
