import sys
import os

# Ensure 'src' is in path to allow imports from ui, utils, etc.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    # Global Exception Handler
    def exception_hook(exctype, value, traceback_obj):
        import traceback
        error_msg = "".join(traceback.format_exception(exctype, value, traceback_obj))
        print("CRITICAL ERROR:", error_msg)
        with open("crash_log.txt", "w") as f:
            f.write(error_msg)
        sys.exit(1)
        
    sys.excepthook = exception_hook

    # Windows taskbar icon fix: Set AppUserModelID to ensure the icon is shown
    if sys.platform == 'win32':
        import ctypes
        myappid = 'com.wavecore.audiomanager.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    app.setApplicationName("Audio Library Manager")
    
    # Load and set application icon (Required for Windows taskbar icon)
    icon_path = os.path.join(current_dir, "resources", "icons", "WaveCore.ico")
    if not os.path.exists(icon_path):
        # Fallback to PNG if ICO is missing
        icon_path = os.path.join(current_dir, "resources", "icons", "WaveCore.png")
    
    if os.path.exists(icon_path):
        from PyQt6.QtGui import QIcon
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    
    # Modern Dark Theme Palette (Fusion style as base)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
