import json
import os
import re
import shutil
from tqdm import tqdm
from datetime import datetime
from dotenv import dotenv_values

config = dotenv_values(".env")
sorted_dir = config["SORTED_DIR"]

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

def has_date(filename):
    for pat in date_patterns:
        m = pat.search(filename)
        if m:
            try:
                year = int(m.group(1))
                if 2000 <= year <= 2025:
                    return True
            except Exception:
                continue
    return False

with open('data/READONLY.json') as f:
    data = json.load(f)

marked_files = [abs_path for abs_path, status in data.items() if status == 3]

no_date = []
for abs_path in tqdm(marked_files, desc="Checking marked files for date"):
    filename = os.path.basename(abs_path)
    if not has_date(filename):
        no_date.append(abs_path)

print(f"Total marked files: {len(marked_files)}")
print(f"Marked files without date in name: {len(no_date)}")

with open('data/no_date_files.txt', 'w', encoding='utf-8') as f:
    for path in no_date:
        f.write(os.path.basename(path) + '\n')

for abs_path in tqdm(marked_files, desc="Copying and renaming"):
    filename = os.path.basename(abs_path)
    name, ext = os.path.splitext(filename)
    year, month, day, time = extract_date_time_uid(filename)
    if not year or not month or not day:
        ts = os.path.getmtime(abs_path)
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
    shutil.copy2(abs_path, dst_path)