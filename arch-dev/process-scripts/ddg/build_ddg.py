import os 
import sys
from tqdm import tqdm
import re
import numpy as np

def reconstuct_all_files_file(file_path, ddg_dot_folder_path):
    """
    this function will adjust the all_files_txt file which is responsible for creating batches for ddg-dot-files processing in case of not completing Processing.
    it will create a list of already processed files and remove them from the all_files_txt file.
    """
    created_dot_files = []
    for dot_file in os.listdir(ddg_dot_folder_path):
        if dot_file.endswith('.dot'):
            basename = os.path.splitext(dot_file)[0]
            created_dot_files.append(basename)
    print(f"Found {len(created_dot_files)} existing DOT files")
    new_lines = []
    removed_count = 0

    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue
            
        # Extract the base filename without extension
        base_filename = "".join(os.path.splitext(os.path.basename(line)))
        # Keep only lines for files that haven't been processed yet
        if base_filename not in created_dot_files:
            new_lines.append(line + '\n')
        else:
            removed_count += 1
    
    # Write the filtered list back to the file
    with open(file_path, 'w') as f:
        f.writelines(new_lines)
    
    print(f"Original file list had {len(lines)} entries")
    print(f"Removed {removed_count} already processed files")
    print(f"Updated file list has {len(new_lines)} entries")
def parse_edge_line(line):
    """
    Extract the source and target node IDs from a DOT edge definition line.
    Equivalent to parseGraphPath() in Java code.
    """
    numbers = re.findall(r'[0-9]+', line)
    if len(numbers) >= 2:
        return int(numbers[0]), int(numbers[1])
    return -1, -1

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

def check_is_edge_line(line):
    """
    Check if a line represents an edge in the DOT file.
    Equivalent to checkIsGraphPath() in Java code.
    """
    pattern = r'^"(\d+)"\s*->\s*"(\d+)"'
    return bool(re.match(pattern, line))

def generate_dot_txt_file(dot_file_path, output_folder):
    """
    generate a dot txt file of single dot file with remaping the node ids
    """

    filename = os.path.basename(dot_file_path)
    output_path = os.path.join(output_folder, f"{filename}.txt")
    edge_list = []
    with open(dot_file_path, "r") as dot_file:
        for line in dot_file:
            line = line.strip()
            if check_is_edge_line(line):
                src, dst = parse_edge_line(line)
                if src != -1 and dst != -1:
                    edge_list.append((src, dst))

    # Create mapping from original IDs to sequential IDs
    unique_nodes = sorted(set([node for edge in edge_list for node in edge]))
    
    id_mapping = {orig_id: seq_id for seq_id, orig_id in enumerate(unique_nodes)}
    #remap edges:
    remapped_edges = [(id_mapping[src], id_mapping[dst]) for src, dst in edge_list]
    with open(output_path, "w") as txt_file:
        for src, dst in remapped_edges:
            txt_file.write(f"{src}, {dst}\n")
 
    #print(f"Generated dot txt file for {dot_file_path} at {output_path}")
def generate_ddg_data(dotFiles_folder_path, output_folder):
    """
    parse all the dot files and generate the dot txt files for all of them 
    """
    for item in os.listdir(dotFiles_folder_path):
        item_path = os.path.join(dotFiles_folder_path, item)
        if item.endswith(".dot"):
            print(f"Generating dot txt file for {item}")
            generate_dot_txt_file(item_path, output_folder)

def analyse_node_counts(dotTxtFolderPath):
    """
    this function will analyse the ides of nodes in the .txt files generated from the DOT files to find the most suitable 
    size for the adjancy matrix
    Maximum node ID across all files: 348
    Average node count: 25.238239083750894
    Median node count: 20.0
    90th percentile: 45.0
    95th percentile: 55.0
    99th percentile: 88.0
    """
    max_node_id = 0
    file_counts = []
    
    # Process each file
    for file in os.listdir(dotTxtFoldePath):
        current_max = 0
        with open(os.path.join(dotTxtFoldePath, file)) as f:
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
def apply_metapath(matrix):
    """
    Apply Metapath algorithm to make the matrix symmetric
    
    Args:
        matrix: A numpy array or sparse matrix
        
    Returns:
        A symmetric matrix after applying the Metapath algorithm
    """
    return np.maximum(matrix, matrix.T)
def build_ddj_adj_matrices(dotTxtFolder_path, output_dir, matrix_size=200):
    """
    Build DDG adj matrices from the generated txt filles is single numpy array.
    """
    
    matrices = []
    filenames = []
    for file in tqdm(os.listdir(dotTxtFolder_path), desc="Building adjancy matrices", leave=False):
        filename = file.split(".dot")[0]
        filenames.append(filename)
        try:
                file_path = os.path.join(dotTxtFolder_path, file)
                with open(file_path, "r") as f:
                    data = f.read().splitlines()
                array = np.zeros((matrix_size, matrix_size), dtype=np.uint8)
                for line in data:
                    try:
                        src, dst = map(int, line.split(","))
                        if src < matrix_size and dst < matrix_size:
                            array[src, dst] = 1
                    except ValueError as e:
                        
                        continue
                array = apply_metapath(array)  # Apply Metapath to make it symmetric
                matrices.append(array)

        except Exception as e:
            print(f"Error processing {file}: {e}")
    matrices = np.stack(matrices)
    print(f"Saving matrices with shape {matrices.shape}...")
    np.savez_compressed(os.path.join(output_dir, "ddg_metapath.npz"), matrices=matrices)
    np.save(os.path.join(output_dir, "ddg_filenames.npy"), np.array(filenames))
    
    #np.save(os.path.join(output_dir, "cfg.npy"), matrices)
    print(f"Saved {len(matrices)} matrices to {output_dir}")

if __name__ == "__main__":
    """ reconstuct_all_files_file(
        '../../dataset/ddg/ddg-dot-files/temp/all_files.txt',
        '../../dataset/ddg/ddg-dot-files/'
    ) """
    """ generate_ddg_data(
        "../../dataset/ddg/ddg-dot-files/",
        "../../dataset/ddg/ddg-dot-txt-files"
    ) """
    #generate_dot_txt_file("Sample_9.java.dot", ".")
    #analyse_node_counts("../../dataset/ddg/ddg-dot-txt-files")
    build_ddj_adj_matrices(
        "../../dataset/ddg/ddg-dot-txt-files",
        "../../dataset/ddg/200"
    )