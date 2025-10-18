import os
import numpy as np
import scipy.sparse as sp
from tqdm import tqdm
import sys




def del_file(path):
    ls = os.listdir(path)
    for q in ls:
        c_path = os.path.join(path, q)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)
    print('Directory cleared successfully')
# Helper functions related to sparse matrices
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
    Unpack a packed sparse matrix back into individual sparse matrices
    """
    
    if packed_matrix is None:
        return []
    
    total_rows, cols = packed_matrix.shape
    n_matrices = total_rows // matrix_size
    
    # Initialize matrices list
    matrices = []
    
    print(f"Unpacking {n_matrices} matrices...")
    for i in range(n_matrices):
        start_row = i * matrix_size
        end_row = start_row + matrix_size
        matrix = packed_matrix[start_row:end_row, :]
        matrices.append(matrix)
    
    return matrices

def extract_sparse_matrix(packed_matrix, index, matrix_size=600):
    """
    Extract a single AST matrix from the packed sparse matrix using an index
    
    Args:
        packed_matrix: The packed sparse matrix
        index: Index of the matrix to extract
        matrix_size: Size of each matrix
        
    Returns:
        A single sparse matrix
    """
    start_row = index * matrix_size
    end_row = start_row + matrix_size
    
    # Extract the slice
    matrix = packed_matrix[start_row:end_row, :]
    
    return matrix

def split_sparse(save_path, data_file_path, matrix_size, is_sparse=True):
    """
    Split a sparse matrix file into train/val/test sets
    
    Args:
        save_path: Base path for saving split files
        data_file_path: Path to the sparse matrix .npz or feature  file 
        matrix_size: Size of each individual matrix (e.g., 600)
        is_sparse: Whether the file contains sparse matrices (True) or dense arrays (False)
    """
    print(f"Loading data from {data_file_path}...")
    
    if is_sparse:
        # Load sparse packed matrix
        packed_matrix = sp.load_npz(data_file_path)
        
        # Get dimensions
        total_rows, cols = packed_matrix.shape
        n_matrices = total_rows // matrix_size
        print(f"Loaded {n_matrices} matrices")
     
        # Calculate split indices
        train_idx = int(n_matrices * 0.8)
        val_idx = train_idx + int((n_matrices - train_idx) / 2)
        
        # Split the packed matrix
        train_rows = train_idx * matrix_size
        val_rows = (val_idx - train_idx) * matrix_size
        
        # Extract slices
        train_matrix = packed_matrix[:train_rows, :]
        val_matrix = packed_matrix[train_rows:train_rows+val_rows, :]
        test_matrix = packed_matrix[train_rows+val_rows:, :]
        
        # Save split matrices
        print(f"Saving train set with {train_idx} matrices...")
        sp.save_npz(f"{save_path}train.npz", train_matrix)
        
        print(f"Saving validation set with {val_idx - train_idx} matrices...")
        sp.save_npz(f"{save_path}val.npz", val_matrix)
        
        print(f"Saving test set with {n_matrices - val_idx} matrices...")
        sp.save_npz(f"{save_path}test.npz", test_matrix)
        
        # Print shapes
        print(f"Train shape: ({train_idx} matrices, {train_matrix.shape})")
        print(f"Val shape: ({val_idx - train_idx} matrices, {val_matrix.shape})")
        print(f"Test shape: ({n_matrices - val_idx} matrices, {test_matrix.shape})")
        
    else:
        # For non-sparse files like embeddings
        data = np.load(data_file_path)
        
        if "embeddings" in data:
            css_embeddings = data["embeddings"]
        if "filenames" in data:
            css_filenames = data["filenames"]

        # Standard split for dense arrays
        train, remainder = np.split(css_embeddings, [int(css_embeddings.shape[0] / 10 * 8)], axis=0)
        val, test = np.split(remainder, [int(remainder.shape[0] / 2)], axis=0)
        
        print(f"Train shape: {train.shape}")
        print(f"Val shape: {val.shape}")
        print(f"Test shape: {test.shape}")
        
        np.save(f"{save_path}train.npy", train)
        np.save(f"{save_path}val.npy", val)
        np.save(f"{save_path}test.npy", test)
         # Split filenames the same way as matrices
        train_idx = int(len(css_filenames) * 0.8)
        val_idx = train_idx + int((len(css_filenames) - train_idx) / 2)
    
        train_filenames = css_filenames[:train_idx]
        val_filenames = css_filenames[train_idx:val_idx]
        test_filenames = css_filenames[val_idx:]
    
        print(f"Train filenames: {len(train_filenames)}")
        print(f"Val filenames: {len(val_filenames)}")
        print(f"Test filenames: {len(test_filenames)}")
    
        np.save(f"{save_path}train_filenames.npy", train_filenames)
        np.save(f"{save_path}val_filenames.npy", val_filenames)
        np.save(f"{save_path}test_filenames.npy", test_filenames)

def split_filenames(save_path, filenames_path):
    """
    Split filename arrays consistently with the matrices
    """
    print(f"Loading filenames from {filenames_path}...")
    filenames = np.load(filenames_path, allow_pickle=True)
    
    # Split filenames the same way as matrices
    train_idx = int(len(filenames) * 0.8)
    val_idx = train_idx + int((len(filenames) - train_idx) / 2)
    
    train_filenames = filenames[:train_idx]
    val_filenames = filenames[train_idx:val_idx]
    test_filenames = filenames[val_idx:]
    
    print(f"Train filenames: {len(train_filenames)}")
    print(f"Val filenames: {len(val_filenames)}")
    print(f"Test filenames: {len(test_filenames)}")
    
    np.save(f"{save_path}train_filenames.npy", train_filenames)
    np.save(f"{save_path}val_filenames.npy", val_filenames)
    np.save(f"{save_path}test_filenames.npy", test_filenames)

def split_y(save_path, labels_path):
    """
    Split labels (y values) consistently with the matrices
    """
    print(f"Loading labels from {labels_path}...")
    y_data = np.load(labels_path)
    if "y" in y_data:
        labels = y_data["y"]
    if "filenames" in y_data:
        filenames = y_data["filenames"]
    # Split labels the same way as matrices
    train_idx = int(len(labels) * 0.8)
    val_idx = train_idx + int((len(labels) - train_idx) / 2)
    
    train_labels = labels[:train_idx]
    val_labels = labels[train_idx:val_idx]
    test_labels = labels[val_idx:]
    
    print(f"Train labels: {train_labels.shape}")
    print(f"Val labels: {val_labels.shape}")
    print(f"Test labels: {test_labels.shape}")
    
    np.save(f"{save_path}train_y.npy", train_labels)
    np.save(f"{save_path}val_y.npy", val_labels)
    np.save(f"{save_path}test_y.npy", test_labels)
    # Saving Y filenames
    train_idx = int(len(filenames) * 0.8)
    val_idx = train_idx + int((len(filenames) - train_idx) / 2)
    
    train_filenames = filenames[:train_idx]
    val_filenames = filenames[train_idx:val_idx]
    test_filenames = filenames[val_idx:]
    
    print(f"Train Y filenames: {len(train_filenames)}")
    print(f"Val Y filenames: {len(val_filenames)}")
    print(f"Test Y filenames: {len(test_filenames)}")
    
    np.save(f"{save_path}y_train_filenames.npy", train_filenames)
    np.save(f"{save_path}y_val_filenames.npy", val_filenames)
    np.save(f"{save_path}y_test_filenames.npy", test_filenames)

def split_matrices(save_path, data_file_path, is_css=False):

    data = np.load(data_file_path, allow_pickle=True)
    if is_css:
        if "embeddings" in data:
            css_embeddings = data["embeddings"]
        if "filenames" in data:
            css_filenames = data["filenames"]

        # Standard split for dense arrays
        train, remainder = np.split(css_embeddings, [int(css_embeddings.shape[0] / 10 * 8)], axis=0)
        val, test = np.split(remainder, [int(remainder.shape[0] / 2)], axis=0)
        
        print(f"Train shape: {train.shape}")
        print(f"Val shape: {val.shape}")
        print(f"Test shape: {test.shape}")
        
        np.save(f"{save_path}train.npy", train)
        np.save(f"{save_path}val.npy", val)
        np.save(f"{save_path}test.npy", test)
         # Split filenames the same way as matrices
        train_idx = int(len(css_filenames) * 0.8)
        val_idx = train_idx + int((len(css_filenames) - train_idx) / 2)
    
        train_filenames = css_filenames[:train_idx]
        val_filenames = css_filenames[train_idx:val_idx]
        test_filenames = css_filenames[val_idx:]
    
        print(f"Train filenames: {len(train_filenames)}")
        print(f"Val filenames: {len(val_filenames)}")
        print(f"Test filenames: {len(test_filenames)}")
    
        np.save(f"{save_path}train_filenames.npy", train_filenames)
        np.save(f"{save_path}val_filenames.npy", val_filenames)
        np.save(f"{save_path}test_filenames.npy", test_filenames)
    else:

        matrices = data["matrices"]
        # Calculate split indices
        n_matrices = len(matrices)
        train_idx = int(n_matrices * 0.8)
        val_idx = train_idx + int((n_matrices - train_idx) / 2)

        # Extract slices
        train_matrix = matrices[:train_idx]
        val_matrix = matrices[train_idx:val_idx]  
        test_matrix = matrices[val_idx:] 

            # Save split matrices
        print(f"Saving train set with {train_idx} matrices...")
        np.savez_compressed(f"{save_path}train.npz", matrices=train_matrix)

        print(f"Saving validation set with {val_idx - train_idx} matrices...")
        np.savez_compressed(f"{save_path}val.npz", matrices=val_matrix)

        print(f"Saving test set with {n_matrices - val_idx} matrices...")
        np.savez_compressed(f"{save_path}test.npz", matrices=test_matrix)

        # Print shapes
        print(f"Train shape: ({train_idx} matrices, {train_matrix.shape})")
        print(f"Val shape: ({val_idx - train_idx} matrices, {val_matrix.shape})")
        print(f"Test shape: ({n_matrices - val_idx} matrices, {test_matrix.shape})")
    

def check_output_data(y_path, ast_filenames_path):
    data = np.load(y_path)
    target_filenames = data["filenames"]
    target_data = data["y"]
    
    ast_filenames = np.load(ast_filenames_path, allow_pickle=True)
   # print(len(target_filenames), len(ast_filenames)) Equal
    # Files are in different order
    target_filenames = [f"{filename}.java" for filename in target_filenames]
    target_filenames_to_idx = {filename: idx for idx, filename in enumerate(target_filenames)}
     # Track stats
    found_count = 0
    missing_count = 0
    missing_filenames = []
    reordered_target = np.zeros((len(ast_filenames)), dtype= target_data.dtype)
    for i, filename in enumerate(ast_filenames):
        if filename in target_filenames_to_idx:
            idx = target_filenames_to_idx[filename]
            reordered_target[i] = target_data[idx]
            found_count += 1
        else:
            missing_filenames.append(filename)
            missing_count += 1
    # Print statistics
    print(f"\nReordering Results:")
    print(f"AST filenames: {len(ast_filenames)}")
    print(f"CSS filenames: {len(target_filenames)}")
    print(f"Matches found: {found_count} ({found_count/len(ast_filenames)*100:.2f}%)")
    print(f"Missing embeddings: {missing_count} ({missing_count/len(ast_filenames)*100:.2f}%)")
    
    if missing_count > 0:
        print(f"\nFirst 5 missing filenames:")
        for filename in missing_filenames[:5]:
            print(f"  - {filename}")
    

    
    print(f"\nSaving reordered CSS data to ../dataset/sparse_data/...")
    np.savez("../dataset/sparse_data/reordered_y.npz", 
             filenames=np.array(ast_filenames),
             y=reordered_target)
    
    print(f"Reordered ouput data saved successfully!")
def reorder_css(file_paths, output_path):
    """
    Reorder CSS embeddings based on AST filenames. since AST and CFG and DDG follow the same order
    """
    

    for path in file_paths:
        data = np.load(path, allow_pickle=True)
        basename = os.path.basename(path)
        if basename == "css.npz":
            css_filenames = data["filenames"]
            css_embeddings = data["embeddings"]
        else:
            ast_filenames = data


    css_filename_to_idx = {filename: idx for idx, filename in enumerate(css_filenames)}
     # Track stats
    found_count = 0
    missing_count = 0
    missing_filenames = []
    reordered_embeddings = np.zeros((len(ast_filenames), css_embeddings.shape[1]), dtype=css_embeddings.dtype)
    #reordered_filenames = np.array(ast_filenames)
    for i, filename in enumerate(ast_filenames):
        if filename in css_filename_to_idx:
            idx = css_filename_to_idx[filename]
            reordered_embeddings[i] = css_embeddings[idx]
            found_count += 1
        else:
            missing_filenames.append(filename)
            missing_count += 1
    # Print statistics
    print(f"\nReordering Results:")
    print(f"AST filenames: {len(ast_filenames)}")
    print(f"CSS filenames: {len(css_filenames)}")
    print(f"Matches found: {found_count} ({found_count/len(ast_filenames)*100:.2f}%)")
    print(f"Missing embeddings: {missing_count} ({missing_count/len(ast_filenames)*100:.2f}%)")
    
    if missing_count > 0:
        print(f"\nFirst 5 missing filenames:")
        for filename in missing_filenames[:5]:
            print(f"  - {filename}")
    

    
    print(f"\nSaving reordered CSS data to {output_path}...")
    np.savez(output_path, 
             filenames=np.array(ast_filenames),
             embeddings=reordered_embeddings)
    
    print(f"Reordered CSS data saved successfully!")
def compare_filenames(filenames1, filenames2):
    """
    Compare two filename arrays and print statistics
    """
    filenames1 = np.load(filenames1, allow_pickle=True)
    filenames2 = np.load(filenames2, allow_pickle=True)['filenames']
    print(filenames2[0])
    print(filenames1[0])
    for i in range(len(filenames1)):
        if filenames1[i] != filenames2[i]:
            print(f"Mismatch at index {i}: {filenames1[i]} != {filenames2[i]}")
    print(f"Total filenames in first array: {len(filenames1)}")
    print(f"Total filenames in second array: {len(filenames2)}")    
def analyse_target(target_filepath):
    y_data = np.load(target_filepath, allow_pickle=True)
    total_samples = len(y_data)
    vuln_samples = np.sum(y_data == 1)
    safe_samples = np.sum(y_data == 0)
    
    vuln_percent = (vuln_samples / total_samples) * 100
    safe_percent = (safe_samples / total_samples) * 100
        
        # Print the results
    print("\n=== Target Data Analysis ===")
    print(f"Total samples: {total_samples}")
    print(f"Vulnerable samples (1): {vuln_samples} ({vuln_percent:.2f}%)")
    print(f"Safe samples (0): {safe_samples} ({safe_percent:.2f}%)")
# Example usage
if __name__ == "__main__":
    analyse_target("../dataset/ready/train_y.npy")

    #check_ouput_data("../dataset/target/y.npz", "../dataset/sparse_data/ast_filenames_sparse.npy")
    #compare_filenames("../dataset/ast/400/ast_filenames.npy", "../dataset/sparse_data/reordered_y.npz")
    # Y and ast are not in the same order

    
    """ reorder_css(
        file_paths=[
            "../dataset/ast/400/ast_filenames.npy",
            "../dataset/sparse_data/css.npz"
        ],
        output_path="../dataset/sparse_data/reordered_css.npz"
    ) """
  
    # Prepare output directory
    """
    output_dir = "../dataset/ready"
    del_file(output_dir) # to hele debuggi
    # Define matrix size for unpacking
 
    

     # Set paths to filename files
    cfg_filenames = "../dataset/cfg/200/cfg_filenames.npy"
    ddg_filenames = "../dataset/ddg/200/ddg_filenames.npy"
    ast_filenames = "../dataset/ast/400/ast_filenames.npy"
      # Set paths to input files
      # change to metapath here
    
    ast_path = "../dataset/ast/400/ast_metapath.npz"
    cfg_path = "../dataset/cfg/200/cfg_metapath.npz"
    ddg_path = "../dataset/ddg/200/ddg_metapath.npz"
    # setup independent Files: CSS and Y
    css_path = "../dataset/sparse_data/reordered_css.npz"  # CSS embeddings
    y_path = "../dataset/sparse_data/reordered_y.npz"  # Labels with Filenames
    

    # Split sparse matrices
    print("\nSplitting AST matrices...")
    split_matrices(f"{output_dir}/ast_", ast_path)
    split_filenames(f"{output_dir}/ast_", ast_filenames)
    
    print("\nSplitting CFG matrices...")
    split_matrices(f"{output_dir}/cfg_", cfg_path)
    split_filenames(f"{output_dir}/cfg_", cfg_filenames)
    print("\nSplitting DDG matrices...")
    split_matrices(f"{output_dir}/ddg_", ddg_path)
    split_filenames(f"{output_dir}/ddg_", ddg_filenames)
    # Split embeddings (non-sparse)
    print("\nSplitting CSS embeddings...")
    split_matrices(f"{output_dir}/css_", css_path, is_css=True)
    
    # Split labels
    print("\nSplitting labels...")
    split_y(output_dir + "/", y_path)

    
    print("\nAll data split successfully!") """
