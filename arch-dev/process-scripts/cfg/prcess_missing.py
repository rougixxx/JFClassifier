#!/usr/bin/env python3
# filepath: /home/pain/Desktop/r3i-stuff/pfe/static-code-analysis/jvFinder/process-scripts/cfg/locate_missing.py

import os
import sys
import shutil
from pathlib import Path
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def delete_missing_files(removed_files_path, folder_path):
    with open(removed_files_path, "r") as f:
        removed_files = f.readlines()
    removed_files = [ line.strip() for line in removed_files if line.strip() ]
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        basename = os.path.basename(item_path).split(".")[0] + ".java"
        if os.path.isfile(item_path) and basename in removed_files:
            print(f"Deleting {item_path}")
            os.remove(item_path)
       
        


    
def find_missing_dot_files(java_dir, dot_dir, output_dir=None, copy_files=False):
    """
    Find Java files that don't have corresponding DOT file outputs.
    
    Args:
        java_dir (str): Directory containing Java files
        dot_dir (str): Directory containing DOT files
        output_dir (str): Directory to save results (default is dot_dir/missing)
        copy_files (bool): Whether to copy missing files to output_dir
        reprocess (bool): Whether to attempt reprocessing missing files
    
    Returns:
        list: List of paths to Java files without DOT outputs
    """
    print(f"Scanning for Java files in: {java_dir}")
    print(f"Checking for DOT files in: {dot_dir}")
    
    # Setup output directory
    if output_dir is None:
        output_dir = os.path.join(dot_dir, "missing")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all Java files
    java_files = []
    for root, _, files in os.walk(java_dir):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    print(f"Found {len(java_files)} Java files")
    
    # Find all DOT files
    dot_files = []
    for root, _, files in os.walk(dot_dir):
        for file in files:
            if file.endswith(".dot"):
                # Extract base name without extension
                base_name = os.path.splitext(file)[0]
                dot_files.append(base_name)
    
    print(f"Found {len(dot_files)} DOT files")
    
    # Find missing files
    missing_files = []
    i = 1
    for java_file in java_files:
        base_name = os.path.basename(java_file)
        print(f"Checking {base_name}=== {i}")
        i += 1
        if base_name not in dot_files:
            missing_files.append(java_file)
    
    # Write results
    missing_file_path = os.path.join(output_dir, "missing_files.txt")
    with open(missing_file_path, "w") as f:
        for file in missing_files:
            f.write(f"{file}\n")
    
    print(f"Found {len(missing_files)} Java files without DOT output")
    print(f"Results saved to: {missing_file_path}")
    
    # Copy missing files if requested
    if copy_files and missing_files:
        print(f"Copying missing files to {output_dir}...")
        for file in missing_files:
            dest_file = os.path.join(output_dir, os.path.basename(file))
            shutil.copy2(file, dest_file)
        print(f"Copied {len(missing_files)} files")

    
    return missing_files

if __name__ == "__main__":
    delete_missing_files("../../dataset/removed_files.txt", "../../dataset/ast/ast-dot-txt-files")

    """ find_missing_dot_files(
        "../../dataset/java-files",
        "../../dataset/cfg-dot-files",
        copy_files=True,
    ) 
 """