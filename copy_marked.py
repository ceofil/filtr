import json
import os
import shutil
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
target_dir = os.getenv("TARGET_DIR")


with open('READONLY.json') as f:
    data = json.load(f)

anchor = '2025-04-18 phone media'

dst_paths = {}

for abs_path in data.keys():
    norm_path = os.path.normpath(abs_path)
    parts = norm_path.split(os.path.sep)
    try:
        anchor_idx = [p.lower() for p in parts].index(anchor.lower())
        rel_parts = parts[anchor_idx:]
        rel_path = os.path.join(*rel_parts)
        dst = os.path.join(target_dir, rel_path)
        dst_paths[abs_path] = dst
    except ValueError:
        raise ValueError(f"Anchor not found in path: {abs_path}")

for abs_path, status in tqdm(list(data.items())):
    if status == 3:
        dst = dst_paths[abs_path]
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(abs_path, dst)