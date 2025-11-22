# JFC-WEB-APP – Java Function Classifier Web Application 
Web Application + Django API for Vulnerability Detection

## 📌 Overview  
This web application provides an accessible interface for interacting with the Java Function Vulnerability Classifier model.  
Built using the **Django** framework, the system allows developers to easily submit Java methods and receive instant security assessments without needing to understand or interact directly with the underlying machine learning pipeline.

---

## 🚀 How It Works  
1. **User Inputs Code**  
   Developers paste or type a Java method into the web form.

2. **Backend Processing**  
   The application forwards the submitted code snippet to the backend, where the deployed machine learning model analyzes it.

3. **Model Prediction**  
   The model classifies the Java method as either **SAFE** or **VULNERABLE**, based on learned semantic and structural features.

4. **Results Display**  
   Once the analysis is complete, the user is redirected to a results page showing the prediction clearly and visually.

This workflow demonstrates how the vulnerability detection model can be seamlessly integrated into a practical development tool, helping developers evaluate code security during the development process.


## 🛠️ Features
- Clean and simple UI for submitting Java methods  
- Automatic forwarding of code to the backend classifier  
- Fast, model-driven vulnerability prediction  
- Results displayed in a user-friendly interface  
- No machine learning expertise required to use the tool  


## 📦 Technologies Used
- **Django** – Web framework for backend and rendering pages  
- **HTML/CSS/Bootstrap** – Frontend interface  
- **Python** – Backend logic  
- **Deployed Deep Learning Model** – Classifies Java methods


### 📂 JFC-web-app Structure:
```
├── api-prediction-files
│   ├── ast
│   │   ├── Sample.java.dot
│   │   └── Sample.java.dot.txt
│   ├── cfg
│   │   ├── Sample.java.dot
│   │   └── Sample.java.dot.txt
│   ├── css
│   ├── ddg
│   │   ├── Sample.java.dot
│   │   └── Sample.java.dot.txt
│   ├── npy-files
│   │   ├── ast_matrix.npy
│   │   ├── cfg_matrix.npy
│   │   ├── css_matrix.npy
│   │   └── ddg_matrix.npy
│   └── Sample.java
├── ast-generator
│    
├── classifier
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3
├── manage.py
├── predictApp
│   ├── admin.py
│   ├── apps.py
│   ├── classifier.py
│   ├── forms.py
│   ├── helpers.py
│   ├── migrations
│   ├── models.py
│   ├── mvsa.py
│   ├── special_tokens_list_all_dataset.txt
│   ├── special_tokens_list.txt
│   ├── tests.py
│   ├── unixcoder.py
│   └── views.py
├── prediction-files
│   ├── ast
│   │   ├── Sample.java.dot
│   │   └── Sample.java.dot.txt
│   ├── cfg
│   │   ├── Sample.java.dot
│   │   └── Sample.java.dot.txt
│   ├── css
│   │   └── css.npy
│   ├── ddg
│   │   ├── Sample.java.dot
│   │   └── Sample.java.dot.txt
│   ├── generate_dot_cfg_ddg.sc
│   ├── java-vuln-detection.keras
│   ├── java-vuln-detection_v2.keras
│   ├── npy-files
│   │   ├── ast_matrix.npy
│   │   ├── cfg_matrix.npy
│   │   ├── css_matrix.npy
│   │   ├── css.npy
│   │   └── ddg_matrix.npy
│   ├── Sample.java
│   ├── unixcoder_model
│   │   ├── added_tokens.json
│   │   ├── config.json
│   │   ├── merges.txt
│   │   ├── model.safetensors
│   │   ├── special_tokens_info.json
│   │   ├── special_tokens_map.json
│   │   ├── tokenizer_config.json
│   │   └── vocab.json
│   └── vuln.java
├── README.md
├── requirements.txt
├── static
│   └── assets
│       ├── bootstrap-5.0.2-dist
│       ├── css
│       │   └── bootstrap.min.css
│       └── js
│           └── bootstrap.bundle.min.js
├── templates
│   ├── assets
│   │   └── base.html
│   ├── index.html
│   └── result_page.html
└── unixcoder_model_special
    ├── config.json
    ├── merges.txt
    ├── model.safetensors
    ├── special_tokens_info.json
    ├── special_tokens_map.json
    ├── tokenizer_config.json
    └── vocab.json
