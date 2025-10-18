import json
import os
import re
from helpers import remove_comments_from_code, allman_to_knr_representation, extract_bad_method, create_class_code, rename_method, construct_java_file, append_func_toJson
from helpers import extract_good_methods, remove_java_comments



RAW_DATASET_ROOT = "/home/pain/Desktop/r3i-stuff/pfe/static-code-analysis/data/juliet-test-suite/Java/src/testcases/"
DEST_ROOT = "../juliet-test-suite/"
JSONL_FILE_PATH = "../juliet-test-suite/juliet.jsonl" 
counter = 200
Bad_only_CWEs = ["CWE111", "CWE383", "CWE506", "CWE510"]

def extract_singleTest_cases():
    global counter
    file_pattern = re.compile(r'.*_\d{2}\.java$')
    for dir in os.listdir(RAW_DATASET_ROOT):
        if dir.startswith("CWE"):
            #Create a Folder of CWE with Vuln and Safe dir inside
            cwe_id = dir.split("_")[0]
            if cwe_id in Bad_only_CWEs:
                # Skipping Bad-only CWEs
                continue
            cwe_name = "_".join(dir.split("_")[1:])
            cwe_dir_name = f"{cwe_id}_{cwe_name}"
            cwe_dir_path = os.path.join(DEST_ROOT, cwe_dir_name)
            # Creating Vuln and safe folders under each cwe-id 
            vuln_dir = os.path.join(cwe_dir_path, "vuln")
            safe_dir = os.path.join(cwe_dir_path, "safe")
            os.makedirs(vuln_dir, exist_ok=True)
            os.makedirs(safe_dir, exist_ok=True)
            
            for item in os.listdir(os.path.join(RAW_DATASET_ROOT, dir)):
                # Case of sub folders of 1000 case of each CWE
                if "s0" in item:
                    sub_dir = os.path.join(RAW_DATASET_ROOT, dir, item)
                    for file in os.listdir(sub_dir):
                        if file_pattern.match(file):
                            java_file = os.path.join(sub_dir, file)
                            try:
                                with open(java_file, "r", encoding="utf-8", errors="ignore") as f:
                                    code = f.read()
                                # Normalize code 
                                code = remove_java_comments(code)
                                code = allman_to_knr_representation(code)
                                #Extract the bad method 
                                bad_method = extract_bad_method(code)
                                new_java_file_path = os.path.join(vuln_dir, f"{construct_java_file(counter)['filename']}")
                                new_bad_method = rename_method(bad_method, construct_java_file(counter)['function_name'])
                                new_code = create_class_code(f"Sample_{counter}", new_bad_method)
                                # Saving the bad method in a file 
                     
                                with open(new_java_file_path, 'w', encoding='utf-8') as out_f:
                                    out_f.write(new_code)
                                append_func_toJson(JSONL_FILE_PATH, new_code, 1, cwe_id)
                                counter += 1
                                
                                for index, good_method in  enumerate(extract_good_methods(code)):
                                    new_java_file_path = os.path.join(safe_dir, f"{construct_java_file(counter)['filename']}")
                                    new_good_method = rename_method(good_method, construct_java_file(counter)['function_name'])
                                    new_code = create_class_code(f"Sample_{counter}", new_good_method)
                                    # write the good methods into files 
                                    with open(new_java_file_path, 'w', encoding='utf-8') as out_f:
                                        out_f.write(new_code)
                                    append_func_toJson(JSONL_FILE_PATH, new_code, 0, cwe_id)
                                    counter += 1
    
                                print(f"✅ Processed {file}")
                                
            

                            except Exception as e:
                                print(f"Error reading {java_file}: {e}")
                            continue
                    # There is no Sub-fodlers s0*       
                else:
                    if file_pattern.match(item):
                        java_file = os.path.join(RAW_DATASET_ROOT, dir, item)
                        try:
                            with open(java_file, "r", encoding="utf-8", errors="ignore") as f:
                                code = f.read()
                            # Normalize code 
                            code = remove_java_comments(code)
                            code = allman_to_knr_representation(code)
                            #Extract the bad method 
                            bad_method = extract_bad_method(code)
                            new_java_file_path = os.path.join(vuln_dir, f"{construct_java_file(counter)['filename']}") # java ext is already added in the construct_java_file function
                            new_bad_method = rename_method(bad_method, construct_java_file(counter)['function_name'])
                            new_code = create_class_code(f"Sample_{counter}", new_bad_method)
                            # Saving the bad method in a file 
                            with open(new_java_file_path, 'w', encoding='utf-8') as out_f:
                                out_f.write(new_code)
                            append_func_toJson(JSONL_FILE_PATH, new_code, 1, cwe_id)
                            counter += 1
                            
                            for index, good_method in  enumerate(extract_good_methods(code)):
                                new_java_file_path = os.path.join(safe_dir, f"{construct_java_file(counter)['filename']}")
                                new_good_method = rename_method(good_method, construct_java_file(counter)['function_name'])
                                new_code = create_class_code(f"Sample_{counter}", new_good_method)
                                # write the good methods into files 
                                with open(new_java_file_path, 'w', encoding='utf-8') as out_f:
                                    out_f.write(new_code)
                                append_func_toJson(JSONL_FILE_PATH, new_code, 0, cwe_id)
                                counter += 1

                            print(f"✅ Processed {item}")

                        except Exception as e:
                            print(f"Error reading {java_file}: {e}")
                        continue

if __name__ == "__main__":

    extract_singleTest_cases()
