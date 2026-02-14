import os
import hashlib

def get_file_hash(path):
    hasher = hashlib.md5()
    with open(path, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

vault_path = r"C:\Users\Luis Alberto Gómez\Music\WaveCore Vault"
files_by_hash = {}

for root, dirs, files in os.walk(vault_path):
    for name in files:
        full_path = os.path.join(root, name)
        try:
            h = get_file_hash(full_path)
            if h not in files_by_hash:
                files_by_hash[h] = []
            files_by_hash[h].append(full_path)
        except Exception as e:
            print(f"Error hashing {full_path}: {e}")

print("--- DUPLICATES ---")
for h, paths in files_by_hash.items():
    if len(paths) > 1:
        print(f"Hash: {h}")
        for p in paths:
            print(f"  {p}")
        print()
