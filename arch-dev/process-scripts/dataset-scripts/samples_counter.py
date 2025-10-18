import os
import json

# Configure the root path to your extracted Juliet test suite
JULIET_ROOT = "../juliet-test-suite/"
JSONL_PATH = "../juliet-test-suite/juliet.jsonl"

def find_empty_directories(root_dir=JULIET_ROOT):
    """
    Find directories that have zero files in both 'vuln' and 'safe' sub-folders.
    
    Args:
        root_dir (str): Root directory to search in
    
    Returns:
        list: List of directories with empty vuln/safe sub-folders
    """
    empty_dirs = []
    
    # Walk through all CWE directories
    for dir_name in os.listdir(root_dir):
        dir_path = os.path.join(root_dir, dir_name)
        
        # Check if it's a directory and if it starts with "CWE"
        if os.path.isdir(dir_path) and dir_name.startswith("CWE"):
            vuln_dir = os.path.join(dir_path, "vuln")
            safe_dir = os.path.join(dir_path, "safe")
            
            # Check if both vuln and safe directories exist
            if os.path.isdir(vuln_dir) and os.path.isdir(safe_dir):
                # Count Java files in each directory
                vuln_files = len([f for f in os.listdir(vuln_dir) if f.endswith(".java")])
                safe_files = len([f for f in os.listdir(safe_dir) if f.endswith(".java")])
                
                # If both directories are empty, add to the list
                if vuln_files == 0 and safe_files == 0:
                    empty_dirs.append(dir_name)
    
    return empty_dirs

def report_empty_directories():
    """Find and report directories with empty vuln/safe folders."""
    empty_dirs = find_empty_directories()
    
    if empty_dirs:
        print("\n⚠️ Empty Directories (zero files in both vuln and safe):")
        print("-----------------------------------------------------")
        for dir_name in sorted(empty_dirs):
            print(f" - {dir_name}")
        print(f"\n📊 Total empty directories: {len(empty_dirs)}")
    else:
        print("\n✅ No empty directories found. All CWE directories contain files.")
def count_samples():
    """Count all samples, separated by vulnerable and safe, for each CWE."""
    # Count files directly in the directory structure
    file_counts = {
        "vulnerable": {},
        "safe": {},
        "total_vulnerable": 0,
        "total_safe": 0
    }
    
    # Walk through the directory structure counting .java files
    for root, dirs, files in os.walk(JULIET_ROOT):
        cwe_id = None
        # Extract CWE ID from path (assuming directory names like "CWE78_OS_Command_Injection")
        path_parts = root.split(os.sep)
        for part in path_parts:
            if part.startswith("CWE"):
                cwe_id = part.split("_")[0]
                break
        
        if not cwe_id:
            continue
            
        # Count files in vuln and safe directories
        if "vuln" in root:
            java_files = [f for f in files if f.endswith(".java")]
            if cwe_id not in file_counts["vulnerable"]:
                file_counts["vulnerable"][cwe_id] = 0
            file_counts["vulnerable"][cwe_id] += len(java_files)
            file_counts["total_vulnerable"] += len(java_files)
        
        elif "safe" in root:
            java_files = [f for f in files if f.endswith(".java")]
            if cwe_id not in file_counts["safe"]:
                file_counts["safe"][cwe_id] = 0
            file_counts["safe"][cwe_id] += len(java_files)
            file_counts["total_safe"] += len(java_files)
    
    # Count entries in the JSONL file if it exists
    jsonl_counts = {
        "vulnerable": {},
        "safe": {},
        "total_vulnerable": 0,
        "total_safe": 0
    }
    
    if os.path.exists(JSONL_PATH):
        with open(JSONL_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    cwe_id = entry.get("cwe")
                    target = entry.get("target")
                    
                    if cwe_id:
                        if target == 1:  # Vulnerable
                            if cwe_id not in jsonl_counts["vulnerable"]:
                                jsonl_counts["vulnerable"][cwe_id] = 0
                            jsonl_counts["vulnerable"][cwe_id] += 1
                            jsonl_counts["total_vulnerable"] += 1
                        elif target == 0:  # Safe
                            if cwe_id not in jsonl_counts["safe"]:
                                jsonl_counts["safe"][cwe_id] = 0
                            jsonl_counts["safe"][cwe_id] += 1
                            jsonl_counts["total_safe"] += 1
                except json.JSONDecodeError:
                    continue
    
    # Print results
    print("\n📁 Counts from Directory Structure:")
    print("----------------------------------")
    print("🛑 Vulnerable Samples:")
    for cwe, count in sorted(file_counts["vulnerable"].items()):
        print(f" - {cwe}: {count} files")
    print(f"\n🔢 Total vulnerable Java files: {file_counts['total_vulnerable']}")
    
    print("\n✅ Safe Samples:")
    for cwe, count in sorted(file_counts["safe"].items()):
        print(f" - {cwe}: {count} files")
    print(f"\n🔢 Total safe Java files: {file_counts['total_safe']}")
    
    # Print JSONL counts if the file exists
    if os.path.exists(JSONL_PATH):
        print("\n\n📄 Counts from JSONL File:")
        print("-------------------------")
        print("🛑 Vulnerable Samples in JSONL:")
        for cwe, count in sorted(jsonl_counts["vulnerable"].items()):
            print(f" - {cwe}: {count} entries")
        print(f"\n🔢 Total vulnerable JSONL entries: {jsonl_counts['total_vulnerable']}")
        
        print("\n✅ Safe Samples in JSONL:")
        for cwe, count in sorted(jsonl_counts["safe"].items()):
            print(f" - {cwe}: {count} entries")
        print(f"\n🔢 Total safe JSONL entries: {jsonl_counts['total_safe']}")
# still a function that find the last counter number
if __name__ == "__main__":
     #count_samples()
     report_empty_directories()