import os
import re
import shutil
from tqdm import tqdm
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
target_dir = os.getenv("TARGET_DIR")
sorted_dir = target_dir + "_sorted"

date_patterns = [
    re.compile(r'(\d{4})(\d{2})(\d{2})[_-](\d{6})'),
    re.compile(r'(\d{4})(\d{2})(\d{2})-WA(\d+)'),
    re.compile(r'(\d{4})[-_\s](\d{2})[-_\s](\d{2})'),
    re.compile(r'(\d{4})(\d{2})(\d{2})'),
]

def extract_date_time_uid(filename):
    for pat in date_patterns:
        m = pat.search(filename)
        if m:
            try:
                year = int(m.group(1))
                if 2000 <= year <= 2025:
                    if len(m.groups()) >= 4:
                        return str(year), m.group(2), m.group(3), m.group(4)
                    elif len(m.groups()) == 3:
                        return str(year), m.group(2), m.group(3), None
            except Exception:
                continue
    return None, None, None, None

all_files = []
for root, _, files in os.walk(target_dir):
    for file in files:
        all_files.append(os.path.join(root, file))

for file_path in tqdm(all_files, desc="Copying and renaming"):
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)
    year, month, day, time = extract_date_time_uid(filename)
    if not year or not month or not day:
        ts = os.path.getmtime(file_path)
        dt = datetime.fromtimestamp(ts)
        year = str(dt.year)
        month = f"{dt.month:02d}"
        day = f"{dt.day:02d}"
        time = f"{dt.hour:02d}{dt.minute:02d}{dt.second:02d}"
    time_str = time if time else "time"
    uid = name
    new_filename = f"{year}_{month}_{day}_{time_str}_{uid}{ext}"
    dst_dir = os.path.join(sorted_dir, year, month)
    os.makedirs(dst_dir, exist_ok=True)
    dst_path = os.path.join(dst_dir, new_filename)
    shutil.copy2(file_path, dst_path)