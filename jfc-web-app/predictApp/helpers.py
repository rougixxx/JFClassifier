import os
import re
import subprocess
from django.conf import settings
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch.nn as nn
from transformers import RobertaTokenizer, RobertaModel, RobertaConfig
import torch
from .unixcoder import UniXcoder
from typing import Optional



def remove_java_comments(java_content):

    """
    Remove single-line (//) and multi-line (/* */) comments from Java source code
    while preserving comments inside string literals and character literals.
    
    Args:
        java_content (str): The Java source code as a string
        
    Returns:
        str: Java code with comments removed
    """
    result = []
    i = 0
    in_string = False
    in_char = False
    in_multiline_comment = False
    string_delimiter = None
    escaped = False
    
    while i < len(java_content):
        char = java_content[i]
        
        # Handle escape sequences
        if escaped:
            result.append(char)
            escaped = False
            i += 1
            continue
        
        # Check for escape character
        if char == '\\' and (in_string or in_char):
            escaped = True
            result.append(char)
            i += 1
            continue
        
        # Handle string and character literals
        if char in ['"', "'"] and not in_multiline_comment:
            if not in_string and not in_char:
                # Starting a string or char literal
                if char == '"':
                    in_string = True
                else:
                    in_char = True
                string_delimiter = char
                result.append(char)
            elif char == string_delimiter:
                # Ending the string or char literal
                in_string = False
                in_char = False
                string_delimiter = None
                result.append(char)
            else:
                result.append(char)
            i += 1
            continue
        
        # If we're inside a string or char literal, preserve everything
        if in_string or in_char:
            result.append(char)
            i += 1
            continue
        
        # Handle multi-line comments
        if in_multiline_comment:
            if char == '*' and i + 1 < len(java_content) and java_content[i + 1] == '/':
                in_multiline_comment = False
                i += 2  # Skip both '*' and '/'
                continue
            else:
                # Preserve newlines to maintain line structure
                if char == '\n':
                    result.append(char)
                i += 1
                continue
        
        # Check for start of multi-line comment
        if char == '/' and i + 1 < len(java_content) and java_content[i + 1] == '*':
            in_multiline_comment = True
            i += 2  # Skip both '/' and '*'
            continue
        
        # Check for single-line comment
        if char == '/' and i + 1 < len(java_content) and java_content[i + 1] == '/':
            # Skip until end of line, but preserve the newline
            while i < len(java_content) and java_content[i] != '\n':
                i += 1
            if i < len(java_content):
                result.append(java_content[i])  # Add the newline
                i += 1
            continue
        
        # Regular character
        result.append(char)
        i += 1
    
    return ''.join(result)

def allman_to_knr_representation(contents):
        s, contents = [], contents.split("\n")
        line = 0
        while line < len(contents):
            if contents[line].strip() == "{":
                s[-1] = s[-1].rstrip() + " {"
            else:
                s.append(contents[line])
            line += 1
        return "\n".join(s)
def create_class_code(method):      
    class_parts = [
            f"public class Sample {{",
            f"{method}",
            "}"
        ]


    return "\n\t".join(class_parts)

def generate_ast_data(java_file_path):
    """
    Generate AST DOT and graph data from Java file
    Returns tuple: (dot_file_path, txt_file_path, success)
    """
    try:
        # Define output paths
       
        output_dir = os.path.dirname(java_file_path)
       
        dot_file_path = os.path.join(output_dir, f"ast/Sample.java.dot")
        txt_file_path = os.path.join(output_dir, "ast/Sample.java.dot.txt")
        # Path to your compiled Java program
        java_jar_path = os.path.join(settings.BASE_DIR, "ast-generator/target/ast-generator-1.jar")
        
        # java -jar target/ast-generator-1.jar ../prediction-files/Sample.java ../prediction-files/ast/Sample.java 
        cmd = [
            "java", 
            "-jar", java_jar_path,
            java_file_path,
            os.path.splitext(dot_file_path)[0]
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"AST generation successful")
            print(f"DOT file: {dot_file_path}")
            print(f"TXT file: {txt_file_path}")
            return  txt_file_path, True
        else:
            print(f"AST generation failed: {result.stderr}")
            return  None, False
            
    except subprocess.TimeoutExpired:
        print("AST generation timed out")
        return  None, False
    except Exception as e:
        print(f"Error running AST generator: {e}")
        return  None, False


def extract_java_method_names(java_code):
    """
    Extract method names from Java code
    
    Args:
        java_code (str): The Java source code as a string
        
    Returns:
        list: List of method names found in the code
    """
    method_names = []
    
    # Remove comments first to avoid false matches
    code_without_comments = remove_java_comments(java_code)
    
    # Define patterns for different method types (in order of priority)
    patterns = [
        # Main method (highest priority)
        r'public\s+static\s+void\s+main\s*\(',
        
        # Public static methods
        r'public\s+static\s+(?:[\w<>\[\]]+\s+)?(\w+)\s*\([^)]*\)\s*\{',
        
        # Public methods
        r'public\s+(?:[\w<>\[\]]+\s+)?(\w+)\s*\([^)]*\)\s*\{',
        
        # Protected methods
        r'protected\s+(?:static\s+)?(?:[\w<>\[\]]+\s+)?(\w+)\s*\([^)]*\)\s*\{',
        
        # Private methods
        r'private\s+(?:static\s+)?(?:[\w<>\[\]]+\s+)?(\w+)\s*\([^)]*\)\s*\{',
        
        # Package-private methods (no explicit modifier)
        r'(?:static\s+)?(?:[\w<>\[\]]+\s+)?(\w+)\s*\([^)]*\)\s*\{'
    ]
    
    # Check for main method specifically
    main_pattern = re.compile(r'public\s+static\s+void\s+main\s*\(', re.IGNORECASE)
    if main_pattern.search(code_without_comments):
        method_names.append('main')
    
    # Extract other methods
    for pattern in patterns[1:]:  # Skip main method pattern since we handled it separately
        matches = re.finditer(pattern, code_without_comments, re.IGNORECASE)
        for match in matches:
            if match.groups():
                method_name = match.group(1)
                if method_name and not is_constructor_or_utility(method_name, java_code):
                    method_names.append(method_name)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_methods = []
    for method in method_names:
        if method not in seen:
            seen.add(method)
            unique_methods.append(method)
    
    return unique_methods

def is_constructor_or_utility(method_name, java_code):
    """
    Check if a method name is a constructor or utility method
    
    Args:
        method_name (str): The method name to check
        java_code (str): The Java source code
        
    Returns:
        bool: True if it's a constructor or utility method
    """
    # Extract class name from code
    class_pattern = re.compile(r'(?:public\s+)?class\s+(\w+)', re.IGNORECASE)
    class_match = class_pattern.search(java_code)
    class_name = class_match.group(1) if class_match else "Sample"
    
    # Common utility methods
    utility_methods = {
        'toString', 'equals', 'hashCode', 'clone', 'finalize',
        'getClass', 'notify', 'notifyAll', 'wait', 'compareTo'
    }
    
    # Check if it's a constructor (same name as class)
    is_constructor = (method_name == class_name or 
                     method_name.lower() == class_name.lower())
    
    # Check if it's a utility method
    is_utility = method_name in utility_methods
    
    # Check if it's a getter/setter
    is_getter_setter = (method_name.startswith('get') or 
                       method_name.startswith('set') or 
                       method_name.startswith('is'))
    
    return is_constructor or is_utility or is_getter_setter



def generate_cfg_ddg_dot(java_file_path, output_path, method_name):
    """Generate CFG DOT file using Joern
        ../jvFinder/joern/joern-cli/joern --script prediction-files/cfg/generate_dot_cfg.sc --param inputFilePath=./prediction-files/Sample.java --param outputPath=./prediction-files/cfg/ --methodName=bubbleSort

    """
    try:
        cmd = [
            "../jvFinder/joern/joern-cli/joern",
            "--script", f"{settings.BASE_DIR}/prediction-files/generate_dot_cfg_ddg.sc",
            "--param", f"inputFilePath={java_file_path}",
            "--param", f"outputPath={output_path}",
            "--param", f"methodName={method_name}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=None)
        
        if result.returncode == 0 and os.path.exists(output_path):
            return True
        else:
            print(f"CFG generation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error generating CFG: {e}")
        return False


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


def generate_dot_txt_file(dot_file_path, output_dir):
    """
    Convert node IDs to sequential numbers (0, 1, 2, ...) and save as adjacency list.
    This gives a cleaner representation than the original large node IDs.
    """
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
   
    return True
def apply_metapath(matrix):
    """
    Apply Metapath algorithm to make the matrix symmetric
    
    Args:
        matrix: A numpy array or sparse matrix
        
    Returns:
        A symmetric matrix after applying the Metapath algorithm
    """
    return np.maximum(matrix, matrix.T)
def build_adj_matrix(dot_txt_file_path, output_dir,  file_name, matrix_size=200):
    """
    Build CFG adj matrix from the generated txt file in single numpay array.
    """    
    matrix = np.zeros((matrix_size, matrix_size), dtype=np.uint8)
    try:        
        with open(dot_txt_file_path, "r") as f:
            data = f.read().splitlines()
        for line in data:
            try:
                src, dst = map(int, line.split(","))
                if 0 <= src < matrix_size and 0 <= dst < matrix_size:
                    matrix[src, dst] = 1
            except ValueError:
                continue
        matrix = apply_metapath(matrix)  # Apply metapath
        matrix_output_path = os.path.join(output_dir, f"{file_name}_matrix.npy")
        np.save(matrix_output_path, matrix)
        return matrix_output_path, True
    except FileNotFoundError:
        print(f"Error: File not found: {dot_txt_file_path}")
        return  None, False
    except Exception as e:
        print(f"Error processing {dot_txt_file_path}: {e}")
        return  None, False
    

def preprocess_code_for_tokeniezation(code_snippet):
        """
        Preprocess the code snippet before tokenization
        
        Args:
            code_snippet: Raw Java code string
            
        Returns:
            Preprocessed code string
        """
        # Remove excessive whitespace
        code_snippet = re.sub(r'\s+', ' ', code_snippet.strip())
        
        # Handle special characters that might affect tokenization
        code_snippet = code_snippet.replace('\t', ' ')
        code_snippet = code_snippet.replace('\n', ' ')
        
        return code_snippet
def generate_code_embedding(code_snippet, model, device):
    window_size = 450
    overlap = 150
    windows = []
    init_tokens = model.tokenizer.tokenize(code_snippet)
    if (len(init_tokens) <= 508): # for special chars added by the unixcoder interface. Just check the unixcoder.py code to understand 
             tokens_ids = model.tokenize([code_snippet], max_length=512, mode="<encoder-only>", padding=True)
             source_ids = torch.tensor(tokens_ids).to(device)
             with torch.no_grad():  # Disable gradient calculation for inference
                tokens_embeddings, code_embedding = model(source_ids)
             code_embedding = code_embedding.cpu().detach().numpy()
            
    else: # Here Processing long code
             windows = []
             window_embeddings = []
             for i in range(0, len(init_tokens), window_size - overlap):
                 end_idx = min(i + window_size, len(init_tokens))
                 window_tokens = init_tokens[i:end_idx]
                 if len(window_tokens) < 100:
                     continue
                # Convert tokens back to string for processing
                 window_text = model.tokenizer.convert_tokens_to_string(window_tokens)
                 windows.append(window_text)
             for window in windows:
                 tokens_ids = model.tokenize([window], max_length=512, mode="<encoder-only>", padding=True)
                 source_ids = torch.tensor(tokens_ids).to(device)
                 with torch.no_grad():
                    _, window_embedding = model(source_ids)
                 window_embeddings.append(window_embedding.cpu().detach().numpy())
            
                # Combine window embeddings (with average pooling)
             if window_embeddings:
                code_embedding = np.mean(np.vstack(window_embeddings), axis=0, keepdims=True)
                
             else:
                # Fallback for edge cases - just use truncated version
                tokens_ids = model.tokenize([code_embedding], max_length=512, mode="<encoder-only>", padding=True)
                source_ids = torch.tensor(tokens_ids).to(device)
                with torch.no_grad():
                    _, code_embedding = model(source_ids)
                code_embedding = code_embedding.cpu().detach().numpy()
            
            # Optional: Free memory
             if torch.cuda.is_available():
                torch.cuda.empty_cache()
    
    return code_embedding
                 
    

# With No batches
def generate_css(file_path, matrix_output_path):
    #device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    #model = UniXcoder("unixcoder_model", "/kaggle/input/vuln-java-functions-detection/special_tokens_list_all_dataset.txt") # to work without
    #model = UniXcoder("prediction-files/unixcoder_model", "./special_tokens_list.txt")
    device = torch.device('cpu') 
    model = UniXcoder("unixcoder_model_special")
    
    model.to(device)
    with open(file_path, "r", encoding="utf8") as java_file:
            code = java_file.read()
    code_snippet = preprocess_code_for_tokeniezation(code)
    embedding = generate_code_embedding(code_snippet, model, device) # 128 is the optimal
    
    
    print(f"Generated embeddings with shape: {embedding.shape}")
    np.save(matrix_output_path, embedding)
    return True
def unixcoder_downloader():
    tokenizer = AutoTokenizer.from_pretrained("microsoft/unixcoder-base")
    model = AutoModel.from_pretrained("microsoft/unixcoder-base")

    # save the model with its stuff 
    tokenizer.save_pretrained("unixcoder_model")
    model.save_pretrained("unixcoder_model")
def save_model():
    model = UniXcoder("microsoft/unixcoder-base", special_tokens_path="./special_tokens_list_all_dataset.txt")
    model.save_model_with_special_vocab("unixcoder_model_special")

import re


def extract_java_method_name(java_code: str) -> Optional[str]:
    """
    Extract the method name from a Java function definition.
    
    Args:
        java_code (str): String containing Java method code
        
    Returns:
        Optional[str]: Method name if found, None otherwise
    """

    
    # Regex pattern to match Java method declaration
    # Captures method name from: [modifiers] returnType methodName(parameters) {
    method_pattern = r'''
        (?:^|\s)                          # Start of line or whitespace
        (?:public|private|protected)?\s*  # Optional access modifier
        (?:static)?\s*                    # Optional static
        (?:final)?\s*                     # Optional final
        (?:abstract)?\s*                  # Optional abstract
        (?:synchronized)?\s*              # Optional synchronized
        (?:native)?\s*                    # Optional native
        # Return type - covers primitives, objects, arrays, generics
        (?:void|int|long|short|byte|char|float|double|boolean|String|\w+(?:\[\])*|\w+<[^>]+>|\w+)\s+
        (\w+)                             # Method name (captured group)
        \s*\(                             # Opening parenthesis
    '''
    
    match = re.search(method_pattern, java_code, re.VERBOSE | re.MULTILINE)
    
    return match.group(1) if match else None



if __name__ == "__main__":
   #unixcoder_downloader()
   #save_model()
   extract_java_method_name()
