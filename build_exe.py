import os
import subprocess
import sys
import shutil

# Configuration
APP_NAME = "WaveCore"
ENTRY_POINT = os.path.join("WaveCore", "src", "main.py")
ICON_PATH = os.path.join("WaveCore", "src", "resources", "icons", "WaveCore.ico")
RESOURCES_SRC = os.path.join("WaveCore", "src", "resources")

def build():
    print(f"--- Building {APP_NAME} v2.0.0 ---")
    
    # Ensure dist folder is cleanable or managed by PyInstaller
    if os.path.exists("dist"):
        print("Cleaning old dist folder...")
        # PyInstaller handles it with --noconfirm usually, but we keep it tidy
    
    # Base command for PyInstaller
    # We use --onefile for a single portable executable
    # We use --windowed to avoid the console window
    # We use --add-data to bundle the resources
    # We use --paths to include the src directory in the search path for imports
    
    # Note: On Windows, use ; to separate paths in --add-data
    data_sep = ";" if os.name == 'nt' else ":"
    
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", APP_NAME,
        "--icon", ICON_PATH,
        "--add-data", f"{RESOURCES_SRC}{data_sep}resources",
        "--paths", os.path.join("WaveCore", "src"),
        ENTRY_POINT
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n" + "="*40)
        print("BUILD COMPLETED SUCCESSFULLY!")
        print(f"Executable located at: {os.path.abspath(os.path.join('dist', APP_NAME + '.exe'))}")
        print("="*40)
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: PyInstaller failed with exit code {e.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    if not os.path.exists(ENTRY_POINT):
        print(f"Error: Entry point {ENTRY_POINT} not found.")
        sys.exit(1)
    
    # Check for icon
    if not os.path.exists(ICON_PATH):
        print(f"Warning: Icon {ICON_PATH} not found. Proceeding without custom icon.")
        # Remove icon from cmd if needed, but build() will handle it or fail
        
    build()
