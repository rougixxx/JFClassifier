# JFClassifier

JFClassifier is a deep learning model for Java vulnerability detection. It is a replication of the JFinder architecture with a key modification: replacing DFG with DDG to better capture semantic relationships in code.

## Features
- Leverages multiple code representations:
  - AST (Abstract Syntax Tree)
  - CFG (Control Flow Graph)
  - DDG (Data Dependence Graph)
  - CSS (Code Snippet Sequence using UniXcoder)
- Quadruple multi-view self-attention for feature fusion
- CNN + MLP for final classification
- MetaPath module to enhance graph connectivity

## Dataset Construction
Our dataset is built by combining three major open-source vulnerability benchmarks to create a diverse and representative corpus for Java vulnerability detection:
- **Juliet Test Suite (SARD)** – Synthetic Java test cases covering 112+ CWEs. We extracted and preprocessed Non-Class-Based and Bad-Only cases by normalizing formatting, removing comments, wrapping functions into standalone Java classes, and exporting them into JSONL format with labels and CWE IDs.
- **OWASP Benchmark Project** – A runnable Java web application containing ~3,000 intentionally vulnerable test cases. We followed the same extraction and preprocessing pipeline to produce consistent JSONL entries.
- **Finetuning LLMs for Vulnerability Detection Dataset** – Public dataset from the authors of the paper, adapted to match our preprocessing format.

After cleaning and unifying all sources, we constructed a final dataset containing:
- **69,850 Java functions total**
- **49,846 safe samples**
- **20,004 vulnerable samples**
All samples are stored in a standardized JSONL format with fields:
```
{
"function": "<java_code_snippet>",
"target": 0/1, # 0 for safe and 1 for vulnerable
"cwe": "CWE_ID"
}
```
This dataset is used to train and evaluate our JFClassifier model.
## Model Architecture and Design
**JFClassifier** is a deep learning model for Java vulnerability detection. It is a replication of the [**JFinder**](JFinder_novel_architecture_for_java_vulnerability_identification.pdf) architecture, with a key modification: replacing **Data Flow Graphs (DFG)** with **Data Dependence Graphs (DDG)**.  

<img width="1506" height="525" alt="jfinder" src="https://github.com/user-attachments/assets/7d6be946-b441-4c38-86d0-846d8f8d0bf6" />

>[!NOTE]
> For Full details of Architecture and implementation, please check [my thesis report](../my_thesis.pdf) 

The model leverages multiple code representations to capture both syntactic and semantic information:
- **AST (Abstract Syntax Tree):** Represents the hierarchical syntactic structure of the code.  
- **CFG (Control Flow Graph):** Captures all possible execution paths.  
- **DDG (Data Dependence Graph):** Models variable definitions, modifications, and usage relationships.  
- **CSS (Code Snippet Sequence):** Encodes semantic information using the pre-trained transformer model **UniXcoder** from Microsoft.


### Feature Extraction
AST, CFG, DDG, and CSS are extracted and encoded into matrices representing structural and semantic code features. 
- AST: we used [JavaParser](https://javaparser.org/) an open-source library which provides you with an Abstract Syntax Tree of your Java code.
- CFG and DDG: we used [Joern](https://joern.io/) an open-source tool designed for the robust analysis of source code, bytecode, and binary code, with support for multiple.programming languages, including Java.
- CSS: we used the [uniXcoder](https://huggingface.co/microsoft/unixcoder-base) transfromer for generating code embeddings.

### Quad Self-Attention Layer  
After extracting the structural representations (AST, CFG, and DDG) and the semantic representation (CSS), these views must be integrated to capture location-specific features and enhance the representation of code. To achieve this, we employ
a Multi-View Self-Attention (MVSA) encoder, an extension of the multi-head attention mechanism.

### MetaPath Module  
Enhances graph connectivity by introducing **length-2 MetaPaths** with reverse edges between connected nodes. This improves graph completeness, reduces sparsity, and strengthens representation learning.

### Classification  
The fused matrix is passed through a **CNN** followed by a **Fully Connected Neural Network (MLP)** to output the final vulnerability classification.

### Highlights
- Combines **structural (AST, CFG, DDG)** and **semantic (CSS)** code information.  
- Uses **multi-head and multi-view self-attention** for advanced feature fusion.  
- MetaPath module reduces overfitting and improves graph-based learning.

