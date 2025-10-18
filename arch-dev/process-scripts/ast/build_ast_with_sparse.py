import os
import numpy as np
import scipy.sparse as sp
import matplotlib.pyplot as plt
import sys
from tqdm import tqdm

"""

Maximum node ID across all files: 3089
Average node count: 255.97429953349933
Median node count: 179.0
90th percentile: 501.0
95th percentile: 606.9499999999971
99th percentile: 809.0
"""

def analyze_ast_node_counts(dotTxtfolderPath):
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
    files_under_400 = sum(1 for count in file_counts if count <= 400)
    percentage_under_400 = (files_under_400 / len(file_counts)) * 100 if file_counts else 0
    # Analyze the distribution
    import matplotlib.pyplot as plt
    plt.hist(file_counts, bins=50)
    plt.title('Distribution of AST Node Counts')
    plt.xlabel('Number of Nodes')
    plt.ylabel('Number of Files')
    plt.axvline(x=np.percentile(file_counts, 95), color='r', linestyle='--', label='95th percentile')
    plt.legend()
    plt.savefig('cfg_node_distribution.png')
    
    print(f"Maximum node ID across all files: {max_node_id}")
    print(f"Average node count: {np.mean(file_counts)}")
    print(f"Median node count: {np.median(file_counts)}")
    print(f"90th percentile: {np.percentile(file_counts, 90)}")
    print(f"95th percentile: {np.percentile(file_counts, 95)}")
    print(f"99th percentile: {np.percentile(file_counts, 99)}")
    print(f"Percentage of files with ≤ 400 nodes: {percentage_under_400:.2f}%")
    print(f"Number of files with ≤ 400 nodes: {files_under_400} out of {len(file_counts)}")
    
    return file_counts

def build_ast(input_dir, output_dir, matrix_size=600):
    """
    Process AST dot.txt files and save them as sparse matrices.
    
    Args:
        input_dir: Directory containing the dot.txt files
        output_dir: Directory to save the output
        matrix_size: Size of each adjacency matrix (default: 200x200)
    """
    
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of dot.txt files
    filenames = [f for f in os.listdir(input_dir) if f.endswith(".dot.txt")]
    
    # Initialize list to store sparse matrices
    sparse_matrices = []
    filenames = []
    for file in tqdm(os.listdir(input_dir), desc="Processing AST files"):
        filename = file.split(".dot")[0]
        filenames.append(filename)
        try:
            file_path = os.path.join(input_dir, file)
            
            # Read data
            with open(file_path) as f:
                data = f.read().splitlines()
            
            # Use sparse representation for memory efficiency
            row_indices = []
            col_indices = []
            
            for line in data:
                try:
                    src, dst = map(int, line.split(","))
                    if 0 <= src < matrix_size and 0 <= dst < matrix_size:
                        row_indices.append(src)
                        col_indices.append(dst)

                except ValueError:
                    print(file)
                    continue
            # Skip if no valid edges
            if not row_indices:
                print(file)
                print("No valid edges")
                continue
            
           
           
            
            # Create sparse matrix
            values = np.ones(len(row_indices), dtype= np.uint8)
            sparse_matrix = sp.csr_matrix(
                (values, (row_indices, col_indices)), 
                shape=(matrix_size, matrix_size)
            )
            
            # Add to list
            sparse_matrices.append(sparse_matrix)

            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    # Save the matrices in sparse format
    if sparse_matrices:
        # Create a block diagonal sparse matrix to store all matrices efficiently
        print(f"Saving {len(sparse_matrices)} matrices...")
        
        # Save sparse matrices
        output_path = os.path.join(output_dir, "ast_sparse.npz")
        
        # Pack the matrices into a single sparse matrix for storage
        packed_matrix = pack_sparse_matrices(sparse_matrices, matrix_size)
        sp.save_npz(output_path, packed_matrix)
        
        # Save corresponding filenames
        np.save(os.path.join(output_dir, "ast_filenames_sparse.npy"), filenames)
        
        print(f"Saved {len(sparse_matrices)} AST matrices to {output_path}")
    else:
        print("No valid matrices to save")

def pack_sparse_matrices(matrices, matrix_size):
    """
    Pack multiple sparse matrices into a single sparse matrix for storage
    """

    
    n_matrices = len(matrices)
    if n_matrices == 0:
        return None
    
    # For a single matrix, just return it
    if n_matrices == 1:
        return matrices[0]
    
    # Create a packed representation
    rows = []
    cols = []
    data = []
    
    for i, matrix in enumerate(matrices):
        # Convert to COO format for easier extraction
        coo = matrix.tocoo()
        
        # Offset rows to create block diagonal structure
        offset_rows = coo.row + (i * matrix_size)
        
        rows.extend(offset_rows)
        cols.extend(coo.col)
        data.extend(coo.data)
    
    # Create the packed sparse matrix
    return sp.csr_matrix(
        (data, (rows, cols)), 
        shape=(n_matrices * matrix_size, matrix_size)
    )

def unpack_sparse_matrices(packed_matrix, matrix_size):
    """
    Unpack a packed sparse matrix back into individual matrices
    """
   
    
    if packed_matrix is None:
        return []
    
    total_rows, cols = packed_matrix.shape
    n_matrices = total_rows // matrix_size
    
    matrices = []
    for i in range(n_matrices):
        start_row = i * matrix_size
        end_row = start_row + matrix_size
        matrix = packed_matrix[start_row:end_row, :]
        matrices.append(matrix)
    
    return len(matrices)

if __name__ == "__main__":
    build_ast(
        "../../dataset/ast/ast-dot-txt-files",
        "../../dataset/ast/",
         matrix_size=600,
         )
    #analyze_ast_node_counts("../../dataset/ast/ast-dot-txt-files")
         
    print(unpack_sparse_matrices(sp.load_npz("../../dataset/ast/ast_sparse.npz"), 600))
    #analyze_ast_node_counts("../dot-txt-files")
#Sample_57093.java.dot.txt got fked up

    