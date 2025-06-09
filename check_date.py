import os
import re
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
target_dir = os.getenv("TARGET_DIR")

date_patterns = [
    re.compile(r'\d{8}_\d{6}'),
    re.compile(r'\d{8}-WA\d+'),
    re.compile(r'(\d{4})[-_\s](\d{2})[-_\s](\d{2})'),
    re.compile(r'(\d{4})(\d{2})(\d{2})'),
]

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

all_files = []
for root, _, files in os.walk(target_dir):
    for file in files:
        all_files.append(os.path.join(root, file))

no_date = []

for file_path in tqdm(all_files, desc="Checking files"):
    filename = os.path.basename(file_path)
    if not has_date(filename):
        no_date.append(file_path)

print(f"Total files: {len(all_files)}")
print(f"Files without date in name: {len(no_date)}")

with open('no_date_files.txt', 'w', encoding='utf-8') as f:
    for path in no_date:
        f.write(os.path.basename(path) + '\n')