from transformers import AutoTokenizer, AutoModel
import nltk
import re
from unixcoder import UniXcoder
import torch
import os
import sys
from tqdm import tqdm
import jsonlines
import numpy as np

def use_json_file(json_file_path):
     code_snippets = []
     filenames = []
     with open(json_file_path, 'r', encoding='utf8') as f:
            entries = list(jsonlines.Reader(f))
            for idx, entry in enumerate(tqdm(entries, desc="Loading JSONL entries")):
                try:
                    code = entry["function"]
                    code_snippets.append(preprocess_code(code))
            
                except Exception as e:
                    print(f"Error processing entry {idx}: {e}")
     return code_snippets
def preprocess_code(code_snippet):
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
def unixcoder_downlader():
    tokenizer = AutoTokenizer.from_pretrained("microsoft/unixcoder-base")
    model = AutoModel.from_pretrained("microsoft/unixcoder-base")

    # save the model with its stuff 
    tokenizer.save_pretrained("unixcoder_model")
    model.save_pretrained("unixcoder_model")
def generate_code_embeddings(code_snippets, model, device, batch_size):
    embeddings = []
    for i in range(0, len(code_snippets), batch_size):
         # Creating a batch of 
         batch = code_snippets[i:i+batch_size]
         tokens_ids = model.tokenize(batch, max_length=512, mode="<encoder-only>", padding=True)
         source_ids = torch.tensor(tokens_ids).to(device)
         with torch.no_grad():  # Disable gradient calculation for inference
            tokens_embeddings, func_embeddings = model(source_ids)
         batch_embeddings = func_embeddings.cpu().detach().numpy()
         embeddings.append(batch_embeddings)
    if embeddings:
        return np.vstack(embeddings)
    else:
        return np.array([])


def batch_generate_css(input_path, output_path ):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    #model = UniXcoder("unixcoder_model", "../../dataset/special_tokens_list_all_dataset.txt")
    model = UniXcoder("unixcoder_model")
    model.to(device)
    files = os.listdir(input_path) # Geating java files
    code_snippets = []
    filenames = []

    for file in tqdm(files, desc="Processing java files"):
        file_path = os.path.join(input_path, file)
        try:
             with open(file_path, "r", encoding="utf8") as java_file:
                  code = java_file.read()
                  code_snippets.append(preprocess_code(code))
                  filenames.append(file)
        except Exception as e:
             print(f"Error reading {file}: {e}")
    print("Generating Embeddings...")
    #  to implement the generate_css function
    embeddings = generate_code_embeddings(code_snippets, model, device, batch_size=64) # 128 is the optimal
    print(f"Generated embeddings with shape: {embeddings.shape}")
    np.savez(f"{output_path}/css.npz", 
             embeddings=embeddings, 
             filenames=np.array(filenames))

    print(f"Embeddings saved to {output_path}")


def find_optimal_batch_size(model, device):
    """Find the largest batch size that fits in memory"""
    # Start with a conservative batch size
    batch_size = 8 
    sample_code = """
    public void processData(List<String> data) {
        if (data == null || data.isEmpty()) {
            return;
        }
        
        for (String item : data) {
            // Process each item
            process(item);
        }
    }
    """
    
    # Try increasing until we hit memory limits
    while True:
        try:
            # Create a batch of the same code
            test_batch = [sample_code] * batch_size
            print(f"in Batch {batch_size}")    
            # Try to process it
            tokens_ids = model.tokenize(test_batch, max_length=512, mode="<encoder-only>")
            source_ids = torch.tensor(tokens_ids).to(device)
        
            with torch.no_grad():
                model(source_ids)
            
            print(f"Batch size {batch_size} works")
            batch_size *= 2  # Try a larger batch
            
            # Clean up memory
            torch.cuda.empty_cache()
            
        except RuntimeError as e:
            # We hit the limit, go back to the previous working size
            optimal_size = batch_size // 2
            print(f"Optimal batch size: {optimal_size}")
            return optimal_size
def log_code_length_statistics(code_snippets, model):
    """Analyze and log statistics about code lengths in the dataset

Code length statistics:
  Min length: 22 tokens
  Max length: 3173 tokens
  Average length: 200.2 tokens
  Snippets exceeding 512 tokens: 2624 (3.8%)
Code length distribution saved to code_length_distribution.png
    
    """
    lengths = []
    for code in code_snippets:
        tokens = model.tokenizer.tokenize(code)
        lengths.append(len(tokens))
    
    print(f"Code length statistics:")
    print(f"  Min length: {min(lengths)} tokens")
    print(f"  Max length: {max(lengths)} tokens")
    print(f"  Average length: {sum(lengths)/len(lengths):.1f} tokens")
    print(f"  Snippets exceeding 512 tokens: {sum(1 for l in lengths if l > 512)} ({sum(1 for l in lengths if l > 512)/len(lengths)*100:.1f}%)")
    
    # Optional: plot length distribution
    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 5))
        plt.hist(lengths, bins=50)
        plt.axvline(x=512, color='r', linestyle='--')
        plt.title('Code Length Distribution')
        plt.xlabel('Number of tokens')
        plt.ylabel('Count')
        plt.savefig('code_length_distribution.png')
        print("Code length distribution saved to code_length_distribution.png")
    except ImportError:
        pass


if __name__ == "__main__":
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = UniXcoder("unixcoder_model")
    model.to(device)
    code_snippets = use_json_file("../../dataset/dataset.jsonl")
    log_code_length_statistics(code_snippets, model)
    #batch_generate_css("../../dataset/java-files", "../../dataset/css")

    