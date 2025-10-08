# Java Function Classifier

A custom VSCode extension that checks Java functions for security vulnerabilities by sending the code to a Django-based REST API.

## Features
- Select Java code and run vulnerability analysis
- Integration with REST API (`/api/predict/`)
- Displays prediction (`SAFE` / `VULNERABLE`) inside VSCode

## Usage
1. Run your Django backend: `python manage.py runserver`
2. In VSCode, open a Java file.
3. Select code → `Ctrl+Shift+P` → ****.

## Requirements
- Django backend running locally
- REST API available at `http://127.0.0.1:8000/api/predict`
