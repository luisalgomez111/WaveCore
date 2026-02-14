
import PyInstaller.__main__
import os

project_root = r"d:\WaveCore\WaveCore"
entry_point = os.path.join(project_root, "src", "main.py")
resources_src = os.path.join(project_root, "src", "resources")
resources_dst = "resources"

# Verify paths
if not os.path.exists(entry_point):
    print(f"Error: Entry point not found at {entry_point}")
    exit(1)

# Add Miniforge3 Library/bin to PATH for DLL resolution
os.environ["PATH"] = r"C:\Users\Public\Miniforge3\Library\bin" + os.pathsep + os.environ["PATH"]

# Build command arguments
args = [
    entry_point,
    '--name=WaveCore',
    '--onefile',
    '--noconsole',
    f'--paths={os.path.join(project_root, "src")}',
    f'--add-data={resources_src}{os.pathsep}{resources_dst}',
    '--clean',
    '--distpath=dist',
    '--workpath=build',
    '--specpath=.',
    # Excludes to save size if possible, though PyInstaller is usually good at this
    '--exclude-module=tkinter', 
]

print(f"Running PyInstaller with args: {args}")

PyInstaller.__main__.run(args)
