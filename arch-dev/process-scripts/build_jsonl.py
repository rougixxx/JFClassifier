import os
import json
import random
from tqdm import tqdm
import sys
import re
n = 0

def generate_java_files(json_path, java_dir):
    class_pattern = re.compile(r'public\s+class\s+(\w+)')

    with open(json_path, "r", encoding="utf8") as f:
        data = f.readlines()
    for line in data:
        entry = json.loads(line)
        java_code = entry.get("function", "")
        match = class_pattern.search(java_code)
        if match:
            class_name = match.group(1)
            file_name = f"{class_name}.java"
        with open(os.path.join(java_dir, file_name), "w", encoding="utf8") as f:
                f.write(java_code)
   
    
def shuffle_json(json_path):
    try:
        with open(json_path, "r", encoding="utf8") as f:
            data = f.readlines()
    
        # Shuffle
        print(f"Shuffling {len(data)} lines...")
        random.shuffle(data)
        # Write back
        print(f"Writing shuffled data back to {json_path}")
        with open(json_path, "w", encoding="utf8") as f:
            for line in data:
                f.write(line)
        print(f"Successfully shuffled {len(data)} lines in {json_path}")
        return True
        
    except Exception as e:
        print(f"Error shuffling file {json_path}: {e}")
        return False
        

def clear_folder(path): # this function delete all files in a folder recuservily
    ls = os.listdir(path)
    for q in ls:
        c_path = os.path.join(path, q)
        if os.path.isdir(c_path):  # If it is a folder, then call it recursively
            clear_folder(c_path)
        else:  # If it is a file, delete it directly
            os.remove(c_path)
    print('The file has been cleared')



def combine_jsonl_files(input_files, output_file):
    # Check that all input files exist
    for file_path in input_files:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input jsonl file not found: {file_path}")
    
    # Create directory for output file if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Read all data from input files
    print(f"Reading {len(input_files)} input files...")
    combined_data = []
    
    for json_file in input_files:
        print(f"Processing file: {json_file}")
        try:
            with open(json_file, "r", encoding="utf8") as f:
                lines = f.readlines()
            for line in tqdm(lines, desc=f"Processing {json_file}"):
                combined_data.append(line)
                    
        except Exception as e:
            print(f"Error reading file {json_file}: {e}")
    
    
    # Write combined data
    print(f"Writing {len(combined_data)} entries to {output_file}...")
    with open(output_file, "w", encoding="utf8") as f:
        for line in tqdm(combined_data, desc="Writing"):
            f.write(line)
    
    print(f"Successfully combined {len(input_files)} files into {output_file}")
    print(f"Total entries: {len(combined_data)}")
    
    return len(combined_data)

# Example usage
if __name__ == "__main__":
    """ # Combine three specific files
    input_files = [
        "../../dataset/juliet-test-suite/juliet.jsonl",
        "../../dataset/owasp-benchmark/owasp_benchmark.jsonl",
        "../../dataset/vul-llm-finetuning/llm_finetuning.jsonl",
    ]
    
    output_file = "../dataset/dataset.jsonl"
    
    combine_jsonl_files(
        input_files=input_files,
        output_file=output_file,
    ) """
   

    #shuffle_json("../dataset/dataset.jsonl")
    #generate_java_files("../dataset/dataset.jsonl", "../dataset/java-files/")