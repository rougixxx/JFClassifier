import os
import json
import re
from helpers import remove_java_comments, allman_to_knr_representation, create_class_code, append_func_toJson, construct_java_file, rename_method
import sys


RAW_DATASET_ROOT = "/home/pain/Desktop/r3i-stuff/pfe/static-code-analysis/data/jsonl-java-code/"
DEST_ROOT = "../vul-llm-finetuning/"
JSONL_FILE_PATH = "../vul-llm-finetuning/llm_finetuning.jsonl" 
counter = 65815

# Example of NO CWE: "cwe": "NVD-CWE-noinfo NVD-CWE-Other
def extract_llm_finetuning_dataset(root_dir, jsonl_path):
    global counter
    stats = {
        "total_processed": 0,
        "vuln": 0,
        "safe": 0,
        "cwes": {}
    }

    with open(jsonl_path, 'w', encoding='utf-8') as output_json_file:
        for file in os.listdir(root_dir):
            if file.endswith(".jsonl"):
                file_path = os.path.join(root_dir, file)
                print(f"Processing file: {file_path}...")
                
                with open(file_path, "r", encoding="utf-8") as json_file:    
                    for line in json_file:
                        try:
                            entry = json.loads(line)
                            if entry["cwe"] not in ["NVD-CWE-noinfo", "NVD-CWE-Other"]:
                                cwe = entry["cwe"].split("-")[0] +  entry["cwe"].split("-")[1]
                            else:
                                cwe = "no-cwe"
                            function = entry["code"]    
                            target = entry["target"]    
                            
                            cwe_dir_path = os.path.join(DEST_ROOT, cwe)
            # Creating Vuln and safe folders under each cwe-id 
                            vuln_dir = os.path.join(cwe_dir_path, "vuln")
                            safe_dir = os.path.join(cwe_dir_path, "safe")
                            os.makedirs(vuln_dir, exist_ok=True)
                            os.makedirs(safe_dir, exist_ok=True)
                            if cwe not in stats["cwes"]:
                                stats["cwes"][cwe] = {"vuln": 0, "safe": 0}
                           # Normalize Code
                            function = remove_java_comments(function)
                            function = allman_to_knr_representation(function)
                                # Creating the code Class
                            new_method = rename_method(function, construct_java_file(counter)['function_name'])
                            new_code = create_class_code(f"Sample_{counter}", new_method)  
                            if target == 1:
                                    new_java_file_path = os.path.join(vuln_dir, f"{construct_java_file(counter)['filename']}")
                                    stats["vuln"] += 1
                                    stats["cwes"][cwe]["vuln"] += 1
                            else:
                                    new_java_file_path = os.path.join(safe_dir, f"{construct_java_file(counter)['filename']}")
                                    stats["safe"] += 1
                                    stats["cwes"][cwe]["safe"] += 1
                            with open(new_java_file_path, 'w', encoding='utf-8') as out_f:
                                    out_f.write(new_code)   
                            append_func_toJson(JSONL_FILE_PATH, new_code, target, cwe)
                            counter += 1
                            stats["total_processed"] += 1
                                # Test then readjust :)
                        except json.JSONDecodeError:
                            print(f"Skipping invalid JSON line in {file_path}")
                        except KeyError as e:
                            print(f"Missing key in entry: {e}")
                        except Exception as e:
                            print(f"Error processing entry: {e}")
     # Print statistics
    print("\n=== Processing Complete ===")
    print(f"Total samples processed: {stats['total_processed']}")
    print(f"Vulnerable samples: {stats['vuln']}")
    print(f"Safe samples: {stats['safe']}")
    print("\nBreakdown by CWE:")
    
    for cwe, counts in sorted(stats["cwes"].items()):
        print(f"{cwe}: {counts['vuln']} vulnerable, {counts['safe']} safe")




if __name__ == "__main__":
    extract_llm_finetuning_dataset(RAW_DATASET_ROOT, JSONL_FILE_PATH)