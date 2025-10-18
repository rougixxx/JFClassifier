import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dense, Embedding, Lambda, Reshape
from tensorflow.keras.layers import Input, concatenate, Dropout

def extract_sparse_features(sparse_matrix, max_features=100):
    """Extract meaningful features from sparse matrix"""
    if sp.issparse(sparse_matrix):
        # Convert to COO format for easier manipulation
        coo = sparse_matrix.tocoo()
        
        # Extract features
        features = []
        
        # 1. Non-zero count
        features.append(coo.nnz)
        
        # 2. Density
        features.append(coo.nnz / (coo.shape[0] * coo.shape[1]))
        
        # 3. Row sums (degree centrality for graphs)
        row_sums = np.array(sparse_matrix.sum(axis=1)).flatten()
        features.extend(row_sums[:min(len(row_sums), max_features//3)])
        
        # 4. Column sums
        col_sums = np.array(sparse_matrix.sum(axis=0)).flatten()
        features.extend(col_sums[:min(len(col_sums), max_features//3)])
        
        # 5. Non-zero values statistics
        if coo.nnz > 0:
            features.extend([
                np.mean(coo.data),
                np.std(coo.data),
                np.min(coo.data),
                np.max(coo.data)
            ])
        else:
            features.extend([0, 0, 0, 0])
        
        # Pad or truncate to max_features
        if len(features) < max_features:
            features.extend([0] * (max_features - len(features)))
        else:
            features = features[:max_features]
            
        return np.array(features, dtype=np.float32)
    else:
        # If not sparse, extract similar features from dense matrix
        features = []
        features.append(np.count_nonzero(sparse_matrix))
        features.append(np.count_nonzero(sparse_matrix) / sparse_matrix.size)
        
        row_sums = np.sum(sparse_matrix, axis=1)
        col_sums = np.sum(sparse_matrix, axis=0)
        
        features.extend(row_sums[:min(len(row_sums), max_features//3)])
        features.extend(col_sums[:min(len(col_sums), max_features//3)])
        
        non_zero_vals = sparse_matrix[sparse_matrix != 0]
        if len(non_zero_vals) > 0:
            features.extend([
                np.mean(non_zero_vals),
                np.std(non_zero_vals),
                np.min(non_zero_vals),
                np.max(non_zero_vals)
            ])
        else:
            features.extend([0, 0, 0, 0])
        
        if len(features) < max_features:
            features.extend([0] * (max_features - len(features)))
        else:
            features = features[:max_features]
            
        return np.array(features, dtype=np.float32)

# Process your sparse matrices
def process_sparse_data(data, max_features=200):
    """Process array of sparse matrices"""
    processed = []
    for matrix in data:
        features = extract_sparse_features(matrix, max_features)
        processed.append(features)
    return np.array(processed)

# Load and process sparse data
x_train_dfg_raw = np.load("data/ready/dfg_train.npy", allow_pickle=True)
x_train_cfg_raw = np.load("data/ready/cfg_train.npy", allow_pickle=True)
x_train_ast_raw = np.load("data/ready/ast_train.npy", allow_pickle=True)

x_train_dfg = process_sparse_data(x_train_dfg_raw, max_features=200)
x_train_cfg = process_sparse_data(x_train_cfg_raw, max_features=200)
x_train_ast = process_sparse_data(x_train_ast_raw, max_features=500)  # Larger for AST

# Same for validation and test sets
x_val_dfg_raw = np.load("data/ready/dfg_val.npy", allow_pickle=True)
x_val_cfg_raw = np.load("data/ready/cfg_val.npy", allow_pickle=True)
x_val_ast_raw = np.load("data/ready/ast_val.npy", allow_pickle=True)

x_val_dfg = process_sparse_data(x_val_dfg_raw, max_features=200)
x_val_cfg = process_sparse_data(x_val_cfg_raw, max_features=200)
x_val_ast = process_sparse_data(x_val_ast_raw, max_features=500)

x_test_dfg_raw = np.load("data/ready/dfg_test.npy", allow_pickle=True)
x_test_cfg_raw = np.load("data/ready/cfg_test.npy", allow_pickle=True)
x_test_ast_raw = np.load("data/ready/ast_test.npy", allow_pickle=True)

x_test_dfg = process_sparse_data(x_test_dfg_raw, max_features=200)
x_test_cfg = process_sparse_data(x_test_cfg_raw, max_features=200)
x_test_ast = process_sparse_data(x_test_ast_raw, max_features=500)