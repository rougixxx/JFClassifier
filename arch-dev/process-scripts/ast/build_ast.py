import os
import os
import numpy as np
import gc
from tqdm import tqdm
import sys
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix

def build_ast_in_batches(input_dir, output_dir, matrix_size=600, batch_size=5000):
    """
    Build AST matrices in batches and save them with corresponding filenames
    
    Args:
        input_dir: Directory containing .dot.txt files
        output_dir: Where to save the output
        matrix_size: Size of each matrix (n×n)
        batch_size: Number of files to process in each batch
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    # Created batch for saving RAM
    # Get list of files
    filenames = [f for f in os.listdir(input_dir) if f.endswith(".dot.txt")]
    total_files = len(filenames)
    
    print(f"Found {total_files} files to process")
    
    # Process in batches
    for batch_start in tqdm(range(0, total_files, batch_size), desc="Processing batches"):
        batch_end = min(batch_start + batch_size, total_files)
        batch_files = filenames[batch_start:batch_end]
        
        # Process this batch
        batch_arrays = []
        batch_filenames = []  # Store filenames corresponding to matrices
        
        for filename in tqdm(batch_files, desc=f"Batch {batch_start//batch_size}", leave=False):
            try:
                file_path = os.path.join(input_dir, filename)
                # Read file in one go (more efficient)
                with open(file_path) as f:
                    data = f.read().splitlines()
                
                # Using zeros is memory efficient for sparse matrices
                array = np.zeros((matrix_size, matrix_size), dtype=np.uint8)  
                # Process each line
                for line in data:
                    try:
                        sor, des = map(int, line.split(","))
                        if 0 <= sor < matrix_size and 0 <= des < matrix_size:
                            array[sor, des] = 1
                        # No else:break which would skip valid edges after an invalid one
                    except ValueError:
                        continue
                
                # Add to batch
                batch_arrays.append(array)
                batch_filenames.append(filename)  # Store the filename
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
        
        # Skip empty batches
        if not batch_arrays:
            continue
            
        # Stack arrays (more efficient than concatenate)
        batch_data = np.stack(batch_arrays)
        
        # Save this batch with filenames
        batch_num = batch_start // batch_size
        out_path = os.path.join(output_dir, f"ast_batch_{batch_num}.npz")
        
        # Save both the matrices and filenames in the same .npz file
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
        gc.collect()  # Force garbage collection
def apply_metapath(matrix):
    """
    Apply Metapath algorithm to make the matrix symmetric
    
    Args:
        matrix: A numpy array or sparse matrix
        
    Returns:
        A symmetric matrix after applying the Metapath algorithm
    """
    return np.maximum(matrix, matrix.T)

def build_ast(input_dir, output_dir, matrix_size=400):
    os.makedirs(output_dir, exist_ok=True)
    # Created batch for saving RAM
    # Get list of files
    filenames = []
    matrices = []
    for file in tqdm(os.listdir(input_dir), desc="Processing AST files"):
        filename = file.split(".dot")[0]
        filenames.append(filename)
         
        try:
            file_path = os.path.join(input_dir, file)
            # Read file in one go (more efficient)
            with open(file_path) as f:
                data = f.read().splitlines()
            array = np.zeros((matrix_size, matrix_size), dtype=np.uint8) 
            for line in data:
                    try:
                        src, dst = map(int, line.split(","))
                        if 0 <= src < matrix_size and 0 <= dst < matrix_size:
                            array[src, dst] = 1
                        # No else:break which would skip valid edges after an invalid one
                    except ValueError:
                        continue
            array = apply_metapath(array)  # Apply Metapath to make it symmetric
            matrices.append(array)

        except Exception as e:
            print(f"Error reading {file}: {e}")
            break
    if not matrices:
        print("No valid matrices found. Exiting.")
        return
    # Stack matrices
    final_matrices = np.stack(matrices)
    print(f"Saving matrices with shape {final_matrices.shape}...")
    np.savez_compressed(os.path.join(output_dir, "ast_metapath.npz"), matrices=final_matrices)
    np.save(os.path.join(output_dir, "ast_filenames.npy"), np.array(filenames))
    
    print(f"Successfully saved {len(matrices)} matrices to {output_dir}")
    print(f"Final shape: {final_matrices.shape}")

if __name__ == "__main__":
    """ build_ast_in_batches(
        input_dir="../../dataset/ast/ast-dot-txt-files/",
        output_dir="../../dataset/ast/ast-batches",
        matrix_size=600,
        batch_size=6000  # Adjust based on available RAM
    ) """
    build_ast(
        input_dir="../../dataset/ast/ast-dot-txt-files/",
        output_dir="../../dataset/ast/400",

    )