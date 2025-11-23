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
- **Django 5.3** – Web framework for backend and rendering pages  
- **HTML/CSS/Bootstrap** – Frontend interface  
- **Python 3.11** – Backend logic  
- **Deployed Deep Learning Model** – Classifies Java methods


### 📂 JFC-web-app Structure:
```
├── api-prediction-files # the folder used to store the files used for prediction for an API request
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

├── ast-generator # Java code used to generate the AST graph dot files

├── classifier # Main Django application
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3 
├── manage.py
├── predictApp # the main app for using the model for code classification
│   ├── admin.py
│   ├── apps.py
│   ├── classifier.py
│   ├── forms.py
│   ├── helpers.py
│   ├── migrations
│   ├── models.py
│   ├── mvsa.py # Muli-view self attetnion Encoder code
│   ├── special_tokens_list_all_dataset.txt # added more vocab to tokenizer
│   ├── special_tokens_list.txt
│   ├── tests.py
│   ├── unixcoder.py # interface class to work the unixcoder model
│   └── views.py # main logic here
├── prediction-files # Files used for Prediction
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
│   ├── java-vuln-detection.keras # the jfc Trained model
│   ├── java-vuln-detection_v2.keras
│   ├── npy-files # graph features matrices
│   │   ├── ast_matrix.npy
│   │   ├── cfg_matrix.npy
│   │   ├── css_matrix.npy
│   │   ├── css.npy
│   │   └── ddg_matrix.npy
│   ├── Sample.java # the targeted method code
│   ├── unixcoder_model # the pre-trained transformer model config files
│   │   ├── added_tokens.json
│   │   ├── config.json
│   │   ├── merges.txt
│   │   ├── model.safetensors
│   │   ├── special_tokens_info.json
│   │   ├── special_tokens_map.json
│   │   ├── tokenizer_config.json
│   │   └── vocab.json
├── README.md
├── requirements.txt
├── static # static bootsrap files
│   └── assets
│       ├── bootstrap-5.0.2-dist
│       ├── css
│       │   └── bootstrap.min.css
│       └── js
│           └── bootstrap.bundle.min.js
├── templates # HTML templates used for the django-app frontend
│   ├── assets
│   │   └── base.html
│   ├── index.html
│   └── result_page.html
```

### Workflow
1. User pastes a Java function into the form.
2. Django backend saves the code and triggers:
   1. AST generation
   2. CFG generation
   3. DDG generation
   4. CSS encoding with UniXcoder
3.Features are converted into matrices and fed to the JFC model.
4. The model outputs: **SAFE** or **VULNERABLE**
5. User is redirected to a results page displaying the prediction.

### API Usage (Used by the VS Code Extension)
Endpoint
```POST /api/predict```

Request Body
```
{
  "code": "public void method() { ... }"
}
```

Response
```
{
  "prediction": "SAFE/VULNEABLE",
}
```
### Running the Web App
1. Create a Python environment and activate it
```
python3 -m venv venv
source venv/bin/activate

```
2. Install dependencies
```
pip install -r requirements.txt

```
Note: you need to ajdust you requirements file based on your needs and your setup

3. Run migrations
```
python manage.py migrate

```
4. Start server
```
python manage.py runserver

```
the app will  be available at:
```
http://127.0.0.1:8000

```
