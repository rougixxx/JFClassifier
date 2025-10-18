import os
import re
import json
import sys
import pandas as pd
from helpers import remove_java_comments, allman_to_knr_representation, extract_post_method, create_class_code
from helpers import append_func_toJson, construct_java_file, rename_method


RAW_DATASET_ROOT = "/home/pain/Desktop/r3i-stuff/pfe/static-code-analysis/data/BenchmarkJava/src/main/java/org/owasp/benchmark/testcode/"
DEST_ROOT = "../owasp-benchmark/" # to put created java files in it 
JSONL_FILE_PATH = "../owasp-benchmark/owasp_benchmark.jsonl" 
counter = 67149
# meta-data file expectedresults-1.2.csv under RAW_DATASER_ROOT

def extract_owasp_benchmark_dataset(root_dir, jsonl_path):
    global counter
    stats = {
        "total_samples": 0,
        "vuln": 0,
        "safe": 0,
        "cwes": {}
    }
    with open(jsonl_path, "w", encoding="utf-8") as jsonl_output_file:
        metadata = pd.read_csv(f"{root_dir}/expectedresults-1.2.csv")
        metadata.columns = ["test_case", "category", "target", "cwe", "version", "date"]
        #print(metadata.columns.to_list())
        metadata = metadata.drop(["version", "date"], axis=1)
        grouped_cwes = metadata.groupby("cwe")
        for cwe, group in grouped_cwes:
            # grouped by a cwe, each group is a set of test cases
            # group here is a type of Tuple
            vuln_count = sum(group["target"])
            safe_count = len(group) - vuln_count
            stats["cwes"][cwe] = {
                "vuln": vuln_count,
                "safe": safe_count
            }
            stats["total_samples"] += len(group)
            stats["vuln"] += vuln_count
            stats["safe"] += safe_count
            #  Creating CWE Folder
            cwe_dir = os.path.join(DEST_ROOT, f"CWE_{cwe}")
            os.makedirs(cwe_dir, exist_ok=True)
            # Creating Vuln and safe sub-folders
            vuln_dir = os.path.join(cwe_dir, "vuln")
            safe_dir = os.path.join(cwe_dir, "safe")
            os.makedirs(vuln_dir, exist_ok=True)
            os.makedirs(safe_dir, exist_ok=True)
            for index, row in group.iterrows():
                if row["target"] == True:
                    # Vulnerable test case
                    target_dir = vuln_dir
                    target = 1
                else:
                    target_dir = safe_dir
                    target = 0
                with open(os.path.join(root_dir, f"{row['test_case']}.java"), "r", encoding="utf-8", errors="ignore") as benchmark_file:
                    code = benchmark_file.read()
                code = remove_java_comments(code)
                code = allman_to_knr_representation(code) 
                # Extract the method and create a new java file 
                method = extract_post_method(code)
                new_method = rename_method(method, construct_java_file(counter)['function_name'])
               # new_code = create_class_code(f"Sample_{counter}", new_method)
                new_code = create_class_code(f"Sample_{counter}", new_method)
                new_java_file_path = os.path.join(target_dir, f"Sample_{counter}.java")
                with open(new_java_file_path, 'w', encoding='utf-8') as out_f:
                        out_f.write(new_code)   
                append_func_toJson(JSONL_FILE_PATH, new_code, target, f"CWE_{cwe}")
                counter += 1
                print(f"✅ Processed {row['test_case']}")
        
    print("\n=== Processing Complete ===")
    print(f"Total samples processed: {stats['total_samples']}")
    print(f"Vulnerable samples: {stats['vuln']}")
    print(f"Safe samples: {stats['safe']}")
    print("\nBreakdown by CWE:")
    
    for cwe, counts in sorted(stats["cwes"].items()):
        print(f"{cwe}: {counts['vuln']} vulnerable, {counts['safe']} safe")

                




if __name__ == "__main__":
    extract_owasp_benchmark_dataset(RAW_DATASET_ROOT, JSONL_FILE_PATH)
