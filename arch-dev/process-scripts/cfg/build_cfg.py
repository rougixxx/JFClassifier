#!/usr/bin/env python3
# filepath: /home/pain/Desktop/r3i-stuff/pfe/static-code-analysis/jvFinder/process-scripts/cfg/process_cfg_dots.py=
import os
import re
import argparse
from pathlib import Path
from tqdm import tqdm
import sys
import numpy as np
import matplotlib.pyplot as plt
import gc

def parse_edge_line(line):
    """
    Extract the source and target node IDs from a DOT edge definition line.
    Equivalent to parseGraphPath() in Java code.
    """
    numbers = re.findall(r'[0-9]+', line)
    if len(numbers) >= 2:
        return int(numbers[0]), int(numbers[1])
    return -1, -1


def check_is_edge_line(line):
    """
    Check if a line represents an edge in the DOT file.
    Equivalent to checkIsGraphPath() in Java code.
    """
    pattern = r'^"(\d+)"\s*->\s*"(\d+)"'
    return bool(re.match(pattern, line))


def save_edge_to_txt(edge_list, output_dir, filename):
    """
    Save the edge list to a txt file.
    Equivalent to saveEdge() in Java code.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    
    with open(output_path, 'w') as f:
        for src, dst in edge_list:
            f.write(f"{src},{dst}\n")
    
    return output_path


def generate_graph_data(dot_folder_path, output_dir=None):
    """
    Process all DOT files in the given folder, extract edges, and save them to txt files.
    Equivalent to generateGraphData() in Java code. but without remaping node ids
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(dot_folder_path), "cfg-txt-files")
    
    os.makedirs(output_dir, exist_ok=True)
    
    dot_files = []
    for root, _, files in os.walk(dot_folder_path):
        for file in files:
            if file.endswith(".dot"):
                dot_files.append(os.path.join(root, file))
    
    print(f"Found {len(dot_files)} DOT files to process")
    
    processed_files = 0
    for dot_file in tqdm(dot_files, desc="Processing CFG DOT files"):
        try:
            # Get base filename for output
            filename = os.path.basename(dot_file)
            
            # Process the DOT file to extract edges
            max_vertex_number = 0
            edge_list = []
            
            with open(dot_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if check_is_edge_line(line):
                        src, dst = parse_edge_line(line)
                        if src != -1 and dst != -1:
                            edge_list.append((src, dst))
                            max_vertex_number = max(max_vertex_number, max(src, dst))
            
            # Save the edges to a txt file
            output_file = save_edge_to_txt(edge_list, output_dir, f"{filename}.txt")
            
            # Optionally create an adjacency matrix
            # adj_matrix = [[0] * (max_vertex_number + 1) for _ in range(max_vertex_number + 1)]
            # for src, dst in edge_list:
            #     adj_matrix[src][dst] = 1
            
            processed_files += 1
            
        except Exception as e:
            print(f"Error processing {dot_file}: {e}")
    
    print(f"Successfully processed {processed_files} out of {len(dot_files)} DOT files")
    print(f"Results saved to: {output_dir}")

def analyze_node_counts(dotTxtfolderPath):
    """
    this function will analyse the ids of the nodes in the .txt files generated from the DOT files to find the most 
    suitable matrix size for the adjacency matrix.
    Maximum node ID across all files: 495
    Average node count: 34.07985683607731
    Median node count: 23.0
    90th percentile: 70.0
    95th percentile: 84.0
    99th percentile: 125.0
    """
    max_node_id = 0
    file_counts = []
    
    # Process each file
    for file in os.listdir(dotTxtfolderPath):
        current_max = 0
        with open(os.path.join(dotTxtfolderPath, file)) as f:
            data = f.readlines()
            
        # Find max node ID in this file
        for line in data:
            sor, des = map(int, line.replace("\n", "").split(","))
            current_max = max(current_max, sor, des)
        
        file_counts.append(current_max + 1)  # +1 because node IDs start at 0
        max_node_id = max(max_node_id, current_max)
    
    # Analyze the distribution
    import matplotlib.pyplot as plt
    plt.hist(file_counts, bins=50)
    plt.title('Distribution of AST Node Counts')
    plt.xlabel('Number of Nodes')
    plt.ylabel('Number of Files')
    plt.axvline(x=np.percentile(file_counts, 95), color='r', linestyle='--', label='95th percentile')
    plt.legend()
    plt.savefig('ast_node_distribution.png')
    
    print(f"Maximum node ID across all files: {max_node_id}")
    print(f"Average node count: {np.mean(file_counts)}")
    print(f"Median node count: {np.median(file_counts)}")
    print(f"90th percentile: {np.percentile(file_counts, 90)}")
    print(f"95th percentile: {np.percentile(file_counts, 95)}")
    print(f"99th percentile: {np.percentile(file_counts, 99)}")
    
    return file_counts
def generate_dot_txt_file(dot_file_path, output_dir):
    """
    Convert node IDs to sequential numbers (0, 1, 2, ...) and save as adjacency list.
    This gives a cleaner representation than the original large node IDs.
    """
    file_counter = 0
    filename = os.path.basename(dot_file_path)
    output_path = os.path.join(output_dir, f"{filename}.txt")
    # Extract edges with original node IDs
    edge_list = []
    
    with open(dot_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if check_is_edge_line(line):
                src, dst = parse_edge_line(line)
                if src != -1 and dst != -1:
                    edge_list.append((src, dst))
  
    # Create mapping from original IDs to sequential IDs
    unique_nodes = sorted(set([node for edge in edge_list for node in edge]))
    
    id_mapping = {orig_id: seq_id for seq_id, orig_id in enumerate(unique_nodes)}
 
    
    # Remap edges
    remapped_edges = [(id_mapping[src], id_mapping[dst]) for src, dst in edge_list]
    # Save remapped edges
    with open(output_path, 'w') as f:
        for src, dst in remapped_edges:
             f.write(f"{src},{dst}\n")
        #for src, dst in sorted(remapped_edges):
    file_counter += 1
    print(f"Generated dot txt file for {dot_file_path} at {output_path} with count {file_counter}")
           
    
def generate_cfg_data(dotFilesFolderPath, outputFolder):
    for item in os.listdir(dotFilesFolderPath):
        item_path = os.path.join(dotFilesFolderPath, item)
        if item.endswith(".dot"):
            generate_dot_txt_file(item_path, outputFolder)
def build_cfg_adj_matrices_in_batches(dotTxtfolderPath, output_dir, matrix_size=125, batch_size=2000):
    """
    Build CFG adj matrcies   from the generated txt files in batchs due to RAM constrain.

    """
    os.makedirs(output_dir, exist_ok=True)

    filenames = [f for f in os.listdir(dotTxtfolderPath) if f.endswith('.txt')]
    total_files = len(filenames)
    
    print(f"Total files to process: {total_files}")
    
    for batch_start in tqdm(range(0, total_files, batch_size), desc="Processing batches"):
        batch_end = min(batch_start + batch_size, total_files)
        batch_files = filenames[batch_start:batch_end]
        
        batch_arrays = []
        batch_filenames = []
        
        for filename in tqdm(batch_files, desc=f"Batch {batch_start // batch_size}", leave=False):
            try:
                file_path = os.path.join(dotTxtfolderPath, filename)
                with open(file_path, "r") as f:
                    data = f.read().splitlines()
                array = np.zeros((matrix_size, matrix_size))
                for line in data:
                    try:
                        src, dst = map(int, line.split(","))
                        if src < matrix_size and dst < matrix_size:
                            array[src, dst] = 1
                    except ValueError:
                            continue
                batch_arrays.append(array)
                batch_filenames.append(filename)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
        
        if not batch_arrays:
            continue
        
        batch_data = np.stack(batch_arrays)
        batch_num = batch_start // batch_size
        out_path = os.path.join(output_dir, f"ast_batch_{batch_num}.npz")
        
        np.savez_compressed(
            out_path, 
            matrices=batch_data,
            filenames=np.array(batch_filenames)
        )
        
        print(f"\nSaved batch {batch_num} with {len(batch_arrays)} matrices")
        print(f"Sample filenames: {batch_filenames[:3]}...")
        
        # Explicitly free memory
        del batch_arrays
        del batch_filenames
        del batch_data
        gc.collect()
def apply_metapath(matrix):
    """
    Apply Metapath algorithm to make the matrix symmetric
    
    Args:
        matrix: A numpy array or sparse matrix
        
    Returns:
        A symmetric matrix after applying the Metapath algorithm
    """
    return np.maximum(matrix, matrix.T)
def build_cfg_adj_matrices(dotTxtfiles_folder, output_dir,  matrix_size=200):
    """
    Build CFG adj matrcies   from the generated txt files in single numpay array.
    """    
    matrices = []
    filenames = []
    for file in tqdm(os.listdir(dotTxtfiles_folder), desc="Building adjacency matrices", leave=False):
        filename = file.split(".dot")[0]
        filenames.append(filename)
        try:
                file_path = os.path.join(dotTxtfiles_folder, file)
                
                with open(file_path, "r") as f:
                    data = f.read().splitlines()
                array = np.zeros((matrix_size, matrix_size), dtype=np.uint8)
                for line in data:
                    try:
                        src, dst = map(int, line.split(","))
                        if 0 <= src < matrix_size and 0 <= dst < matrix_size:
                            array[src, dst] = 1
                    except ValueError:
                            continue
                array = apply_metapath(array)  # Apply metapath if needed
                matrices.append(array)
        except Exception as e:
                print(f"Error processing {file}: {e}")
    matrices = np.stack(matrices)
    print(f"Saving matrices with shape {matrices.shape}...")
    np.savez_compressed(os.path.join(output_dir, "cfg_metapath.npz"), matrices=matrices)
    np.save(os.path.join(output_dir, "cfg_filenames.npy"), np.array(filenames))
    
    #np.save(os.path.join(output_dir, "cfg.npy"), matrices)
    print(f"Saved {len(matrices)} matrices to {output_dir}")
# Example usage
# build_cfg_adj_matrices("../../dataset/cfg/cfg-dot-txt-files", matrix_size=125)
if __name__ == "__main__":
    #generate_cfg_data("../../dataset/cfg/cfg-dot-files", "../../dataset/cfg/cfg-dot-txt-files")
    #analyze_cfg_node_counts("../../dataset/cfg/cfg-dot-txt-files")# run analysis on the generated txt files
    # build cfg batches with the generated txt files
   """  build_cfg_adj_matrices_in_batches(
        "../../dataset/cfg/cfg-dot-txt-files", 
        "../../dataset/cfg/cfg-batches",
        matrix_size=125 ,
        batch_size=2000
    )
 """
   build_cfg_adj_matrices("../../dataset/cfg/cfg-dot-txt-files","../../dataset/cfg/200" )