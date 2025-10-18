import os
import os
import numpy as np
import gc
from tqdm import tqdm
import sys
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
import scipy.sparse as sp

def build_cfg_with_sparse(input_dir, output_dir, matrix_size=125):

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    # Created batch for saving RAM
    # Get list of files
    filenames = [f for f in os.listdir(input_dir) if f.endswith(".dot.txt")]
    total_files = len(filenames)
    
    print(f"Found {total_files} files to process")
    filenames = []
    sparse_matrices = []
    for file in tqdm(os.listdir(input_dir)):
        filename = file.split(".dot")[0]
        filenames.append(filename)
        try:
            file_path = os.path.join(input_dir, file)
            with open(file_path) as f:
                data = f.read().splitlines()
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
            if not row_indices:
                print(file)
                print("No valid edges")
                continue
        
            values = np.ones(len(row_indices), dtype=np.uint8)
            sparse_matrix = sp.csr_matrix(
                (values, (row_indices, col_indices)), 
                shape=(matrix_size, matrix_size)
            )
            sparse_matrices.append(sparse_matrix)
        except Exception as e:
            print(f"Erorr in Processing {file}: {e}")
    if sparse_matrices:
        print(f"Saving {len(sparse_matrices)} matrices...")
        
        # Save sparse matrices
        output_path = os.path.join(output_dir, "cfg_sparse.npz")
        
        # Pack the matrices into a single sparse matrix for storage
        packed_matrix = pack_sparse_matrices(sparse_matrices, matrix_size)
        sp.save_npz(output_path, packed_matrix)
        
        # Save corresponding filenames
        np.save(os.path.join(output_dir, "cfg_filenames_sparse.npy"), filenames)
        
        print(f"Saved {len(sparse_matrices)} CFG matrices to {output_path}")
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
    """ build_cfg_with_sparse(
        input_dir="../../dataset/cfg/cfg-dot-txt-files/",
        output_dir="../../dataset/cfg/",
    ) """
    print(unpack_sparse_matrices(sp.load_npz("../../dataset/cfg/cfg_sparse.npz"), 125))
    