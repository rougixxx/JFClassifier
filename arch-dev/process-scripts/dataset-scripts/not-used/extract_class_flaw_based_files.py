import os
import shutil
import re

# Customize your paths
JULIET_SRC = "/path/to/Juliet_Test_Suite_Java"
DEST_DIR = "class_based_dataset"

def normalize_name(name):
    return name.replace(" ", "_").replace(":", "").lower()

def get_cwe_id_and_name(filename):
    match = re.match(r"(CWE\d+)_([A-Za-z0-9_]+)", filename)
    if match:
        return match.group(1), match.group(2)
    return None, None

def extract_class_block(code):
    match = re.search(r'public\s+class\s+[\w_]+\s*\{[\s\S]*\}', code)
    return match.group(0) if match else None

def process_class_flaws():
    for root, _, files in os.walk(JULIET_SRC):
        for file in files:
            if file.endswith("_bad.java") or file.endswith("_good1.java"):
                label = "vuln" if "_bad.java" in file else "safe"
                cwe_id, cwe_name = get_cwe_id_and_name(file)
                if not cwe_id:
                    continue

                target_dir = os.path.join(
                    DEST_DIR,
                    normalize_name(f"{cwe_id}_{cwe_name}"),
                    label
                )
                os.makedirs(target_dir, exist_ok=True)

                try:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        code = f.read()

                    class_code = extract_class_block(code)
                    if class_code:
                        dest_file = os.path.join(target_dir, file)
                        with open(dest_file, 'w', encoding='utf-8') as out_f:
                            out_f.write(class_code)
                        print(f"✅ Extracted {file} → {label}")
                    else:
                        print(f"⚠️ Class not found in {file}")

                except Exception as e:
                    print(f"❌ Error with {file}: {e}")

if __name__ == "__main__":
    process_class_flaws()
