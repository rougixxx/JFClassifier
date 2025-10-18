import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter

def analyze_vulnerability_dataset(jsonl_path="../dataset/dataset.jsonl"):
    """
    Analyze the vulnerability dataset from JSONL file
    
    Args:
        jsonl_path: Path to the dataset.jsonl file
        
    Returns:
        Dictionary containing analysis results
    """
    
    # Initialize counters and lists
    targets = []
    sample_names = []
    
    print(f"Reading dataset from: {jsonl_path}")
    
    try:
        with open(jsonl_path, 'r', encoding='utf8') as f:
            data = f.readlines()
        
        print(f"Found {len(data)} entries in dataset")
        
        # Extract targets and sample names
        for entry in data:
            try:
                parsed_entry = json.loads(entry)
                target = parsed_entry.get("target", None)
                
                if target is not None:
                    targets.append(target)
                    
                    # Extract sample name from function definition
                    function_code = parsed_entry.get("function", "")
                    class_def = function_code.splitlines()[0] if function_code else ""
                    
                    # Use regex to extract class name
                    import re
                    class_name_pattern = re.compile(r"\s*public\s+class\s+(\w+_\d+)\s*")
                    match = class_name_pattern.search(class_def)
                    
                    if match:
                        sample_names.append(match.group(1))
                    else:
                        sample_names.append(f"sample_{len(sample_names)}")
                        
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON entry: {e}")
                continue
        
        # Convert to numpy array for analysis
        targets_array = np.array(targets)
        
        # Count vulnerable (1) and safe (0) samples
        unique_values, counts = np.unique(targets_array, return_counts=True)
        
        # Create results dictionary
        results = {
            'total_samples': len(targets),
            'vulnerable_samples': np.sum(targets_array == 1),
            'safe_samples': np.sum(targets_array == 0),
            'unique_values': unique_values.tolist(),
            'counts': counts.tolist(),
            'targets': targets,
            'sample_names': sample_names
        }
        
        # Calculate ratios
        if results['total_samples'] > 0:
            results['vulnerable_ratio'] = results['vulnerable_samples'] / results['total_samples']
            results['safe_ratio'] = results['safe_samples'] / results['total_samples']
        else:
            results['vulnerable_ratio'] = 0
            results['safe_ratio'] = 0
        
        # Print analysis results
        print("\n" + "="*50)
        print("VULNERABILITY DATASET ANALYSIS")
        print("="*50)
        print(f"Total samples: {results['total_samples']:,}")
        print(f"Vulnerable samples (target=1): {results['vulnerable_samples']:,}")
        print(f"Safe samples (target=0): {results['safe_samples']:,}")
        print(f"\nRatios:")
        print(f"  Vulnerable: {results['vulnerable_ratio']:.4f} ({results['vulnerable_ratio']*100:.2f}%)")
        print(f"  Safe: {results['safe_ratio']:.4f} ({results['safe_ratio']*100:.2f}%)")
        
        # Check for class imbalance
        imbalance_ratio = max(results['vulnerable_samples'], results['safe_samples']) / min(results['vulnerable_samples'], results['safe_samples']) if min(results['vulnerable_samples'], results['safe_samples']) > 0 else float('inf')
        print(f"\nClass imbalance ratio: {imbalance_ratio:.2f}:1")
        
        if imbalance_ratio > 2:
            print("⚠️  Dataset is imbalanced! Consider using techniques like:")
            print("   - Oversampling minority class")
            print("   - Undersampling majority class")
            print("   - Class weights in model training")
            print("   - SMOTE or similar techniques")
        else:
            print("✅ Dataset appears reasonably balanced")
        
        return results
        
    except FileNotFoundError:
        print(f"Error: Could not find file {jsonl_path}")
        return None
    except Exception as e:
        print(f"Error reading dataset: {e}")
        return None

def visualize_dataset_distribution(results, save_path=None):
    """
    Create visualizations of the dataset distribution
    
    Args:
        results: Results dictionary from analyze_vulnerability_dataset
        save_path: Optional path to save the plot
    """
    
    if results is None:
        print("No results to visualize")
        return
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Vulnerability Dataset Analysis', fontsize=16, fontweight='bold')
    
    # 1. Bar chart of counts
    labels = ['Safe (0)', 'Vulnerable (1)']
    counts = [results['safe_samples'], results['vulnerable_samples']]
    colors = ['green', 'red']
    
    bars = ax1.bar(labels, counts, color=colors, alpha=0.7, edgecolor='black')
    ax1.set_title('Sample Counts by Class')
    ax1.set_ylabel('Number of Samples')
    
    # Add count labels on bars
    for bar, count in zip(bars, counts):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(counts)*0.01, 
                f'{count:,}', ha='center', va='bottom', fontweight='bold')
    
    # 2. Pie chart of proportions
    ax2.pie(counts, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax2.set_title('Distribution of Vulnerability Classes')
    
    # 3. Ratio comparison
    ratios = [results['safe_ratio'], results['vulnerable_ratio']]
    bars2 = ax3.bar(labels, ratios, color=colors, alpha=0.7, edgecolor='black')
    ax3.set_title('Class Ratios')
    ax3.set_ylabel('Proportion')
    ax3.set_ylim(0, 1)
    
    # Add ratio labels on bars
    for bar, ratio in zip(bars2, ratios):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{ratio:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # 4. Summary statistics
    ax4.axis('off')
    summary_text = f"""
    Dataset Summary:
    
    Total Samples: {results['total_samples']:,}
    
    Safe Samples: {results['safe_samples']:,} ({results['safe_ratio']*100:.1f}%)
    Vulnerable Samples: {results['vulnerable_samples']:,} ({results['vulnerable_ratio']*100:.1f}%)
    
    Imbalance Ratio: {max(counts)/min(counts) if min(counts) > 0 else 'N/A':.2f}:1
    
    Recommendation:
    {'Balanced dataset ✅' if max(counts)/min(counts) < 2 else 'Imbalanced dataset ⚠️'}
    """
    
    ax4.text(0.1, 0.5, summary_text, transform=ax4.transAxes, fontsize=12,
             verticalalignment='center', bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to: {save_path}")
    
    plt.show()



# Example usage
if __name__ == "__main__":
    # Analyze the dataset
    results = analyze_vulnerability_dataset("../dataset/dataset.jsonl")
    
    if results:
        # Create visualizations
        visualize_dataset_distribution(results, save_path="../dataset/dataset_analysis.png")
        

        
        # Save detailed analysis
        import json
        with open("../dataset/dataset_analysis.json", 'w') as f:
            # Remove non-serializable numpy arrays for JSON export
            json_results = {k: v for k, v in results.items() 
                           if k not in ['targets', 'sample_names']}
            json.dump(json_results, f, indent=2)
        
        print(f"\nDetailed analysis saved to: ../dataset/dataset_analysis.json")