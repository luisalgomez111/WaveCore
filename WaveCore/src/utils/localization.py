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
        "dialog_about_text": f"WaveCore Audio Library v{VERSION}",
        "dialog_about_html": f"""
            <h2 style='color: #D75239;'>WaveCore Audio Library</h2>
            <p><b>Version {VERSION}</b> | Build 2026</p>
            <p>WaveCore is a comprehensive solution designed for sound designers, video editors, and music producers requiring fast and efficient management of their audio assets.</p>
            
            <h3>Key Features:</h3>
            <ul>
                <li><b>Local Library Management:</b> Organize, browse, and play your personal audio collection with an optimized interface.</li>
                <li><b>Online Search (Freesound):</b> Access thousands of free sound effects directly from the app. Includes automatic search translation.</li>
                <li><b>Waveform Visualization:</b> Precise preview with visual amplitude representation and interactive navigation (Scrubbing).</li>
                <li><b>Quick Export (Drag & Drop):</b> Select any snippet of the waveform and drag it directly into your favorite DAW or video editor.</li>
                <li><b>Multi-format Support:</b> Compatible with WAV, MP3, OGG, FLAC, AIFF, and more.</li>
            </ul>
            <p>Developed with passion to optimize your creative workflow.</p>
        """,
        "dialog_creator_title": "Creator & License",
        "dialog_creator_text": "Created by Luis Alberto Gómez",
        "dialog_creator_info": "Lead Developer: Luis Alberto Gómez\n\nIntellectual Property of the creator.\n\nLicense:\nPermission granted for personal and professional use.\nUnauthorized redistribution or reverse engineering prohibited.\n\n© 2026 Luis Alberto Gómez. All rights reserved.",
        "dialog_select_folder": "Select Audio Folder",
        "status_loading": "Loading: {}",
        "status_loaded": "Loaded {} tracks.",
        "ctx_new_folder": "New Folder",
        "ctx_rename": "Rename Folder",
        "ctx_delete": "Delete Folder",
        "ctx_rename_file": "Rename File",
        "ctx_rename_file": "Rename File",
        "ctx_delete_file": "Delete File",
        "menu_updates": "Check for Updates",
        "status_no_updates": "You already have the latest version.",
        "status_update_available": "Update Available",
        "status_update_msg": "A new version of WaveCore is available! ({})\n\nDo you want to download the installer now?",
        # Columns
        "col_name": "Name",
        "col_channels": "Channels",
        "col_format": "Format",
        "col_duration": "Duration",
        "col_genre": "Genre",
        "col_duration": "Duration",
        "col_format": "Format",
        "col_bpm": "BPM",
        "col_waveform": "Waveform",
        "dialog_welcome_title": "Welcome to WaveCore",
        "dialog_welcome_html": """
            <h2 style='color: #D75239; margin-bottom: 10px;'>Welcome to WaveCore!</h2>
            <p>Thank you for choosing WaveCore. Here's a quick guide to get you started:</p>
            <ul style='margin-left: 15px;'>
                <li><b>Vault:</b> Your audio files are indexed automatically in the <b>Library</b> tab.</li>
                <li><b>Search:</b> Use the <b>Online</b> tab to find sounds on Freesound directly.</li>
                <li><b>Drag & Drop:</b> Drag any clip or selection from the waveform to your DAW.</li>
            </ul>
            <hr style='border: 0; border-top: 1px solid #333; margin: 15px 0;'>
            <p><b>Useful Links:</b></p>
             <p style='margin-top: 10px;'>🌐 <a href='https://wave-core.vercel.app/' style='color: #D75239; text-decoration: none;'>Official Website (Vercel)</a></p>
             <p>🐙 <a href='https://github.com/luisalgomez111/WaveCore' style='color: #D75239; text-decoration: none;'>GitHub Repository</a></p>
        """,
    },
    "es": {
        "window_title": f"Librería de Audio WaveCore v{VERSION}",
        "library_header": "    BÓVEDA WAVECORE",
        "menu_file": "Archivo",
        "menu_import": "Importar Carpeta...",
        "menu_exit": "Salir",
        "menu_language": "Idioma",
        "menu_help": "Ayuda",
        "menu_about": "Acerca de",
        "menu_creator": "Creador y Licencia",
        "dialog_about_title": "Acerca de WaveCore",
        "dialog_about_text": f"Librería de Audio WaveCore v{VERSION}",
        "dialog_about_html": f"""
            <h2 style='color: #D75239;'>WaveCore Audio Library</h2>
            <p><b>Versión {VERSION}</b> | Build 2026</p>
            <p>WaveCore es una solución integral diseñada para diseñadores de sonido, editores de video y productores musicales que necesitan gestión rápida y eficiente de sus activos de audio.</p>
            
            <h3>Funcionalidades Principales:</h3>
            <ul>
                <li><b>Gestión de Librería Local:</b> Organiza, explora y reproduce tu colección de audio personal con una interfaz optimizada.</li>
                <li><b>Búsqueda Online (Freesound):</b> Accedes a miles de efectos de sonido gratuitos directamente desde la aplicación. Incluye traducción automática de búsquedas.</li>
                <li><b>Visualización de Forma de Onda:</b> Previsualización precisa con representación visual de la amplitud y navegación interactiva (Scrubbing).</li>
                <li><b>Exportación Rápida (Drag & Drop):</b> Selecciona cualquier fragmento de la onda y arrástralo directamente a tu DAW o editor de video favorito.</li>
                <li><b>Soporte Multi-formato:</b> Compatible con WAV, MP3, OGG, FLAC, AIFF y más.</li>
            </ul>
            <p>Desarrollado con pasión para optimizar tu flujo de trabajo creativo.</p>
        """,
        "dialog_creator_title": "Creador y Licencia",
        "dialog_creator_text": "Creado por Luis Alberto Gómez",
        "dialog_creator_info": "Desarrollador Principal: Luis Alberto Gómez\n\nEste software es propiedad intelectual de su creador.\n\nLicencia de Uso:\nSe concede permiso para uso personal y profesional.\nQueda prohibida la redistribución no autorizada o la ingeniería inversa.\n\n© 2026 Luis Alberto Gómez. Todos los derechos reservados.",
        "dialog_select_folder": "Seleccionar Carpeta de Audio",
        "status_loading": "Cargando: {}",
        "status_loaded": "Se cargaron {} archivos.",
        "ctx_new_folder": "Nueva Carpeta",
        "ctx_rename": "Renombrar Carpeta",
        "ctx_delete": "Eliminar Carpeta",
        "ctx_rename_file": "Renombrar Archivo",
        "ctx_rename_file": "Renombrar Archivo",
        "ctx_delete_file": "Eliminar Archivo",
        "menu_updates": "Buscar Actualizaciones",
        "status_no_updates": "Ya tienes la versión más reciente de WaveCore.",
        "status_update_available": "Actualización Disponible",
        "status_update_msg": "¡Hay una nueva versión de WaveCore disponible! ({})\n\n¿Deseas descargar el nuevo instalador ahora?",
        # Columnas
        "col_name": "Nombre",
        "col_channels": "Canales",
        "col_format": "Formato",
        "col_duration": "Duración",
        "col_genre": "Género",
        "col_duration": "Duración",
        "col_format": "Formato",
        "col_bpm": "BPM",
        "col_waveform": "Onda",
        "dialog_welcome_title": "Bienvenido a WaveCore",
        "dialog_welcome_html": """
            <h2 style='color: #D75239; margin-bottom: 10px;'>¡Bienvenido a WaveCore!</h2>
            <p>Gracias por elegir WaveCore. Aquí tienes una guía rápida para comenzar:</p>
            <ul style='margin-left: 15px;'>
                <li><b>Bóveda:</b> Tus archivos se indexan automáticamente en la pestaña <b>Library</b>.</li>
                <li><b>Búsqueda:</b> Usa la pestaña <b>Online</b> para buscar sonidos en Freesound.</li>
                <li><b>Drag & Drop:</b> Arrastra cualquier clip o selección directamente a tu DAW.</li>
            </ul>
            <hr style='border: 0; border-top: 1px solid #333; margin: 15px 0;'>
            <p><b>Enlaces Útiles:</b></p>
             <p style='margin-top: 10px;'>🌐 <a href='https://wave-core.vercel.app/' style='color: #D75239; text-decoration: none;'>Sitio Web Oficial (Vercel)</a></p>
             <p>🐙 <a href='https://github.com/luisalgomez111/WaveCore' style='color: #D75239; text-decoration: none;'>Repositorio en GitHub</a></p>
        """,
    },
    "ru": {
        "window_title": "Менеджер Аудиобиблиотеки v1.0",
        "library_header": "    БИБЛИОТЕКА",
        "menu_file": "Файл",
        "menu_import": "Импорт папки...",
        "menu_exit": "Выход",
        "menu_help": "Справка",
        "menu_about": "О программе",
        "menu_language": "Язык",
        "dialog_about_title": "О программе",
        "dialog_about_text": "Менеджер Аудиобиблиотеки v1.0",
        "dialog_about_info": "Разработано Antigravity.\n\nКредиты:\n- PyQt6\n- SoundFile\n- NumPy\n\nПрофессиональный инструмент для управления звуковыми эффектами.",
        "dialog_select_folder": "Выберите папку библиотеки",
        "status_loading": "Загрузка файлов из {}...",
        "status_loaded": "Загружено {} файлов.",
        "ctx_new_folder": "Добавить категорию",
        "ctx_rename": "Переименовать",
        "ctx_delete": "Удалить",
        "ctx_rename_file": "Переименовать файл",
        "ctx_delete_file": "Удалить файл"
    },
    "zh": {
        "window_title": "音频库管理器 v1.0",
        "library_header": "    库",
        "menu_file": "文件",
        "menu_import": "导入文件夹...",
        "menu_exit": "退出",
        "menu_help": "帮助",
        "menu_about": "关于",
        "menu_language": "语言",
        "dialog_about_title": "关于",
        "dialog_about_text": "音频库管理器 v1.0",
        "dialog_about_info": "由 Antigravity 开发。\n\n致谢：\n- PyQt6\n- SoundFile\n- NumPy\n\n专业的音效管理工具。",
        "dialog_select_folder": "选择库文件夹",
        "status_loading": "正在从 {} 加载文件...",
        "status_loaded": "已加载 {} 个文件。",
        "ctx_new_folder": "添加类别",
        "ctx_rename": "重命名",
        "ctx_delete": "删除",
        "ctx_rename_file": "重命名文件",
        "ctx_delete_file": "删除文件"
    },
    "fr": {
        "window_title": "Gestionnaire de Bibliothèque Audio v1.0",
        "library_header": "    BIBLIOTHÈQUE",
        "menu_file": "Fichier",
        "menu_import": "Importer le dossier...",
        "menu_exit": "Quitter",
        "menu_help": "Aide",
        "menu_about": "À propos",
        "menu_language": "Langue",
        "dialog_about_title": "À propos",
        "dialog_about_text": "Gestionnaire de Bibliothèque Audio v1.0",
        "dialog_about_info": "Développé par Antigravity.\n\nCrédits:\n- PyQt6\n- SoundFile\n- NumPy\n\nUn outil professionnel pour la gestion des effets sonores.",
        "dialog_select_folder": "Sélectionner le dossier de la bibliothèque",
        "status_loading": "Chargement des fichiers de {}...",
        "status_loaded": "{} fichiers chargés.",
        "ctx_new_folder": "Ajouter une catégorie",
        "ctx_rename": "Renommer",
        "ctx_delete": "Supprimer",
        "ctx_rename_file": "Renommer le fichier",
        "ctx_delete_file": "Supprimer le fichier"
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
