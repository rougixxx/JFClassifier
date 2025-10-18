import os
import re
import uuid
from pathlib import Path

# Config
ROOT_DIR = "dataset"  # your root directory of Java files
WRITE_MAPPING = True
MAPPING_FILE = "method_mapping.csv"

method_counter = 0
method_mapping = []

# Regex: match method definitions (simplified)
method_def_pattern = re.compile(r"(public|private|protected)?\s+[\w<>]+\s+(\w+)\s*\(.*?\)\s*{")

def generate_new_name():
    global method_counter
    method_counter += 1
    return f"func_{method_counter:04d}"

def rename_methods_in_file(file_path):
    global method_mapping

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    matches = list(method_def_pattern.finditer(code))
    if not matches:
        return  # skip if no methods found

    new_code = code
    offset = 0  # track index shift due to name replacements

    for match in matches:
        full_match = match.group(0)
        original_name = match.group(2)
        new_name = generate_new_name()

        new_full = full_match.replace(original_name, new_name, 1)
        span = match.span()

        new_code = new_code[:span[0] + offset] + new_full + new_code[span[1] + offset:]
        offset += len(new_full) - len(full_match)

        method_mapping.append((file_path, original_name, new_name))

    # Overwrite file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_code)

def scan_and_rename(root_dir):
    for dirpath, _, files in os.walk(root_dir):
        for fname in files:
            if fname.endswith(".java"):
                rename_methods_in_file(os.path.join(dirpath, fname))

def save_mapping(path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("file,original_name,new_name\n")
        for row in method_mapping:
            f.write(f"{row[0]},{row[1]},{row[2]}\n")

if __name__ == "__main__":
    print(f"🔍 Scanning Java files in {ROOT_DIR}...")
    scan_and_rename(ROOT_DIR)
    print(f"✅ Renamed {method_counter} methods.")
    if WRITE_MAPPING:
        save_mapping(MAPPING_FILE)
        print(f"📄 Mapping saved to {MAPPING_FILE}")
