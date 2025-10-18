import jsonlines
from nltk import word_tokenize
from transformers import RobertaTokenizer
import random
import matplotlib.pyplot as plt
from tqdm import tqdm
import sys

""" This script will extract some extra special tokens vocab to improve the 
    vocability of the unixcoder model for java code with 20% as the sample size taken
 """

functions = []
with open(f"../../dataset/dataset.jsonl", 'r') as dataset_file:
    all_entries = list(jsonlines.Reader(dataset_file))
    total_samples = len(all_entries)
    # Taking random 20% of dataset size
    sample_size = int((total_samples * 20) / 100 )
    sampled_items = random.sample(all_entries, sample_size)
    functions = [item["function"] for item in sampled_items]
   
    # Taking all the dataset
    #functions = [entry["function"] for entry in all_entries]
# Load the Model
tokenizer = RobertaTokenizer.from_pretrained("unixcoder_model")

# Get a list of special words
special_tokens_set = set()
token_growth = []


for count, function in enumerate(tqdm(functions, desc="Processing code samples")):
    tokens = word_tokenize(function)
    initial_size = len(special_tokens_set)
    for token in tokens:
        token_id = tokenizer.convert_tokens_to_ids(token)
        if token_id == 3: # Id: 3 Unkown token for the model 
            special_tokens_set.add(token)
    # Tracking growth of special tokens set every 100 sample
    if count % 50 == 0:
        token_growth.append((count, len(special_tokens_set)))
    if (count + 1) % 200 == 0:
        print(f"Processed {count+1} samples. Found {len(special_tokens_set)} special tokens.")
    
special_tokens_list = list(special_tokens_set)
print(f"Total special tokens found: {len(special_tokens_list)}")
""" # Plot the growth curve
counts, sizes = zip(*token_growth)
plt.figure(figsize=(10, 6))
plt.plot(counts, sizes)
plt.xlabel('Samples processed')
plt.ylabel('Number of unique special tokens')
plt.title('Growth of unique special tokens over samples')
plt.grid(True)
plt.savefig("token_growth.png")
 """
# Write special_tokens_list to text
with open("../../dataset/special_tokens_list.txt", 'w') as f:
    f.write(" ".join(str(i) for i in special_tokens_list))

print(f"Special tokens list saved to ../../dataset/special_tokens_list.txt")