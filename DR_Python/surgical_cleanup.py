import os
import hashlib

def get_file_hash(path):
    hasher = hashlib.md5()
    try:
        with open(path, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    except: return None

vault_path = r"C:\Users\Luis Alberto Gómez\Music\WaveCore Vault"
files_by_hash = {}

all_files = []
for root, dirs, files in os.walk(vault_path):
    for name in files:
        all_files.append(os.path.join(root, name))

for f in all_files:
    h = get_file_hash(f)
    if h:
        if h not in files_by_hash:
            files_by_hash[h] = []
        files_by_hash[h].append(f)

print("--- DUPLICATES TO DELETE (ONLY IF IN FILES OR OTHERS) ---")
for h, paths in files_by_hash.items():
    if len(paths) > 1:
        # We want to keep the one that is IN a category and delete the one in root or FILES
        # Categories are subfolders like Whoosh, Ambiente etc.
        # FILES is the dump folder.
        
        # Sort paths to prefer categorized ones
        paths.sort(key=lambda x: ("\\FILES\\" in x or "\\WaveCore Vault\\" + os.path.basename(x) == x))
        
        # The first ones are categories (hopefully), the last ones are likely duplicates
        to_keep = paths[0]
        to_delete = paths[1:]
        
        print(f"KEEP: {to_keep}")
        for d in to_delete:
            print(f"  DELETE: {d}")
            try:
                os.remove(d)
                print(f"    SUCCESS")
            except Exception as e:
                print(f"    FAILED: {e}")
        print()

# Also delete any file NOT starting with WC - in folders that should have it
special_orphans = [
    r"C:\Users\Luis Alberto Gómez\Music\WaveCore Vault\Ambiente\SteamPipe 3 GhostBlow G#4.wav.mp3"
]

for o in special_orphans:
    if os.path.exists(o):
        print(f"DELETING ORPHAN: {o}")
        try:
            os.remove(o)
            print("  SUCCESS")
        except Exception as e:
            print(f"  FAILED: {e}")
