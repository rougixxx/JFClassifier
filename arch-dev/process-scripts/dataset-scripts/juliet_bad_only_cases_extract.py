import os
import json
import shutil
import re
from helpers import extract_bad_method,  extract_helper_methods, create_class_code, construct_cwe_folder_name, construct_java_file, rename_method  # Import the helper functions
from helpers import remove_comments_from_code, allman_to_knr_representation, remove_java_comments
# ---- USER SETTINGS ----
RAW_DATASET_ROOT = "/home/pain/Desktop/r3i-stuff/pfe/static-code-analysis/data/juliet-test-suite/Java/src/testcases/"
DEST_ROOT = "../juliet-test-suite/"

# ---- BAD-ONLY CWE MAPPINGS ----
BAD_ONLY_CWES = {
    "CWE111": "Direct Use of Unsafe JNI",
    "CWE383": "J2EE Bad Practices: Direct Use of Threads",
    "CWE506": "Embedded Malicious Code",
    "CWE510": "Trapdoor"
}
JSONL_FILE_PATH = "../juliet-test-suite/juliet.jsonl" 


counter = 1

def extract_badOnly_cases():
   # os.makedirs("../julliet-test-suite/", exist_ok=True)
    #for root, dirs, files in os.walk("../../data/juliet-test-suite/Java/src/testcases/"):
    global counter
    for dir in os.listdir(RAW_DATASET_ROOT):
        for cwe_id in BAD_ONLY_CWES:
            if cwe_id in dir:
                #Create a Folder of CWE with Vuln and Safe dir inside
                cwe_dir_name = f"{cwe_id}_{construct_cwe_folder_name(BAD_ONLY_CWES[cwe_id])}"
                cwe_dir_path = os.path.join(DEST_ROOT,cwe_dir_name)
                # Creating Vuln and safe folders under each cwe-id 
                vuln_dir = os.path.join(cwe_dir_path, "vuln")
                safe_dir = os.path.join(cwe_dir_path, "safe")
                os.makedirs(vuln_dir, exist_ok=True)
                os.makedirs(safe_dir, exist_ok=True)
                for item in os.listdir(os.path.join(RAW_DATASET_ROOT,dir)):
                    # need to find all java files inside the bad test cases of each CWE
                    if cwe_id in item and item.endswith(".java"):
                        java_file = os.path.join(RAW_DATASET_ROOT, dir, item)
                        try:
                            with open(java_file, "r", encoding="utf-8", errors="ignore") as f:
                                code = f.read()
                            # Normalize code 
                            code = remove_java_comments(code)
                            code = allman_to_knr_representation(code)
                            # extract the bad Method
                            bad_method = extract_bad_method(code)
                            new_java_file_path = os.path.join(vuln_dir, f"{construct_java_file(counter)['filename']}")
                            new_method = rename_method(bad_method, construct_java_file(counter)['function_name'])
                            new_code = create_class_code(f"Sample_{counter}", new_method)
                            
                            with open(new_java_file_path, 'w', encoding='utf-8') as out_f:
                                # write the renamed Function
                                out_f.write(new_code)
                            json_entry = {
                                "function": new_code,
                                "target": 1,
                                "cwe": cwe_id,
                            }
                            with open(JSONL_FILE_PATH, 'a', encoding='utf-8') as jsonl_file:
                                jsonl_file.write(json.dumps(json_entry) + '\n')

                            print(f"✅ Processed {item}")
                            counter += 1

                        except Exception as e:
                            print(f"Error reading {java_file}: {e}")
                            continue
                    



            

    
if __name__ == "__main__":
    extract_badOnly_cases()
