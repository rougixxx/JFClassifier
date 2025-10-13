# 📘 Java Function Classifier VS Code Extension

## 🧠 Overview
The **Java Function Classifier** is a Visual Studio Code extension designed to analyze and classify Java functions as **Vulnerable** or **Safe**.  
It integrates seamlessly with a **Django REST API** backend that serves a trained machine learning model for vulnerability detection.  

The extension allows developers to test code snippets directly from the VS Code editor — ideal for integrating AI-powered code security into the development workflow.

---

## ⚙️ Features
✅ **Code selection & classification** — Select any Java function and classify it instantly.  
✅ **AI-based vulnerability prediction** — Uses a trained deep learning model deployed on a Django API.  
✅ **Visual highlighting** —  
- 🟥 Red background → *Vulnerable code detected*  
- 🟩 Green background → *Safe code*  
✅ **Progress loader** — Displays a “Processing…” loader while communicating with the backend.  
✅ **Seamless integration** — Works directly in the VS Code editor without leaving your coding environment.

---

## 🏗️ Architecture
<img width="894" height="598" alt="image" src="https://github.com/user-attachments/assets/50bfd66e-fb8c-49e3-9213-d77e7c4e14c4" />

**Workflow:**
1. Developer selects a Java function.  
2. The extension sends the function to the Django REST API.  
3. The backend model analyzes it and predicts *VULNERABLE* or *SAFE*.  
4. The extension highlights the result directly in the editor.

---

## 🚀 Installation

### 1️⃣ Prerequisites
- [Node.js](https://nodejs.org/) ≥ 18  
- [Visual Studio Code](https://code.visualstudio.com/)  
- Django backend running locally (API endpoint: `http://127.0.0.1:8000/api/predict`)

### 2️⃣ Clone this Repository
```bash
git clone https://github.com/rougixxx/JFClassifier
cd JFClassifier
```
### 3️⃣ Install Dependencies
```bash
npm install
```
### 4️⃣ Build the Extension
```bash
npm run compile
```
### 5️⃣ Run in VS Code
- Open the extension folder in VS Code
- Press F5 → a new window “Extension Development Host” will open
- Open a Java file, select some code, and run the command:
```bash
Ctrl + Shift + P → Classify a Function
```
## 🧩 Packaging the Extension
If you want to generate an installable `.vsix` file:
```bash
npm install -g vsce
vsce package # in the folder of the extension
```
This create a file like:
`jfc-0.0.1.vsix`

You can install it locally via:
```bash
code --install-extension jfc-0.0.1.vsix 
```
## 🧰 Usage Example

1. Open any `.java` file in VS Code
2. Select a function or block of code
3. Run the “Classify a function” command
4. The extension sends the code to the Django API and highlights it:

- 🟥 Vulnerable → Red background

- 🟩 Safe → Green background

The prediction result also appears in the VS Code notification popup.

<img width="1920" height="612" alt="jfc1" src="https://github.com/user-attachments/assets/f511575e-7373-48d9-aeda-11d88531a3bb" />

<img width="1816" height="660" alt="jfc2" src="https://github.com/user-attachments/assets/cb13f2ca-4d39-4180-9eed-3ea3b922558e" />

## 🧾 License
MIT License © 2025 — rougixxx
