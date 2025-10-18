from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .forms import JavaCodeForm
from .models import PredictionHistory
from .helpers import (remove_java_comments, allman_to_knr_representation, create_class_code, generate_ast_data, extract_java_method_names, generate_cfg_ddg_dot,
generate_dot_txt_file , build_adj_matrix, generate_css, extract_java_method_name
)
from .classifier import JavaFunctionClassifier
import re
import os
import numpy as np
import torch

#***********************VIEWS********************
def index(request):
    """Main page with the form"""
    form = JavaCodeForm()
    recent_predictions = PredictionHistory.objects.all()[:5]
    
    context = {
        'form': form,
        'recent_predictions': recent_predictions
    }
    return render(request, 'index.html', context)

def predictForm(request):
    """Handle prediction requests"""
    if request.method == 'POST':
        form = JavaCodeForm(request.POST, request.FILES)
        model_path = os.path.join(settings.BASE_DIR, "prediction-files/java-vuln-detection_v2.keras")
        classifier = JavaFunctionClassifier(model_path)
        
        
        if form.is_valid():
            java_code = form.cleaned_data.get('java_code', '')
            java_file = form.cleaned_data.get('java_file')
            
            
            # If file is uploaded, read its content
            if java_file:
                try:
                    java_code = java_file.read().decode('utf-8')
                except UnicodeDecodeError:
                    messages.error(request, 'Error reading file. Please ensure it contains valid text.')
                    return redirect('home')
             
            if java_code:
                # Normalizing and prepossing the code
                java_code = remove_java_comments(java_code)
                java_code = allman_to_knr_representation(java_code)
                java_code = create_class_code(java_code)
                java_file_path = os.path.join(settings.BASE_DIR, "prediction-files/Sample.java")
                with open(java_file_path, 'w', encoding='utf-8') as out_f:
                                    out_f.write(java_code) 
               
                method_name = extract_java_method_name(java_code)
                if method_name is None:
                     messages.error(request, 'Error in Extracting method name')
                     return redirect('home')
                # Generating AST
                ast_dot_txt_path, ast_success = generate_ast_data(java_file_path)
                if not ast_success:
                     messages.error(request, 'Error in generating AST data')
                     return redirect('home')
                #Generating CFG DDG
                cfg_ddg_generation_sucess = generate_cfg_ddg_dot(java_file_path, f"{settings.BASE_DIR}/prediction-files/", method_name)
                if not cfg_ddg_generation_sucess:
                     messages.error(request, 'Error in generating CFG and DDG data')
                     return redirect('home')
                # generating dot txt for CFG,DDG
                cfg_dot_txt_generation_sucess = generate_dot_txt_file(f"{settings.BASE_DIR}/prediction-files/cfg/Sample.java.dot", f"{settings.BASE_DIR}/prediction-files/cfg/")
                if not cfg_dot_txt_generation_sucess:
                     messages.error(request, 'Error in generating CFG DOT TXT File')
                     return redirect('home')
               
                ddg_dot_txt_generation_sucess = generate_dot_txt_file(f"{settings.BASE_DIR}/prediction-files/ddg/Sample.java.dot", f"{settings.BASE_DIR}/prediction-files/ddg/")
                if not ddg_dot_txt_generation_sucess:
                     messages.error(request, 'Error in generating DDG DOT TXT File')
                     return redirect('home')
                # Building adj matrcices for AST, DDG, CFG
                ## AST
                ast_matrix_path, ast_adj_generation = build_adj_matrix(ast_dot_txt_path, f"{settings.BASE_DIR}/prediction-files/npy-files/", "ast", matrix_size=600)
                if not ast_adj_generation:
                     messages.error(request, 'Error in generating AAST adj matrix')
                     return redirect('home')
                ## CFG
                cfg_dot_txt_path = f"{settings.BASE_DIR}/prediction-files/cfg/Sample.java.dot.txt"
                cfg_matrix_path, cfg_adj_generation = build_adj_matrix(cfg_dot_txt_path, f"{settings.BASE_DIR}/prediction-files/npy-files/", "cfg")
                if not cfg_adj_generation:
                     messages.error(request, 'Error in generating CFG adj matrix')   
                     return redirect('home')
                 ## DDG
                ddg_dot_txt_path = f"{settings.BASE_DIR}/prediction-files/ddg/Sample.java.dot.txt"
                ddg_matrix_path, ddg_adj_generation = build_adj_matrix(ddg_dot_txt_path, f"{settings.BASE_DIR}/prediction-files/npy-files/", "ddg")
                if not ddg_adj_generation:
                     messages.error(request, 'Error in generating DDG adj matrix')
                     return redirect('home')
                # Generating CSS
                css_matrix_path = f"{settings.BASE_DIR}/prediction-files/npy-files/css_matrix.npy"
                code_embedding_generation = generate_css(java_file_path, css_matrix_path)
                if not code_embedding_generation:
                     messages.error(request, 'Error in generating CSS matrix')
                     return redirect('home')
     
                # Predicting the sample 
                try:
                     predictionResult = classifier.predict(ast_matrix_path, cfg_matrix_path, ddg_matrix_path, css_matrix_path)
                     PredictionHistory.objects.create(
                        java_code=java_code,  
                        prediction=predictionResult,
                    )
                    
                     context = {
                        'java_code': java_code,
                        'prediction': predictionResult,
                        'form': JavaCodeForm()  # Fresh form for new prediction
                    } 
                except Exception as e:
                    messages.error(request, f'Error during prediction: {str(e)}')
                    return redirect('home')                   
                return render(request, 'result_page.html', context)
                                
    
            else:
                messages.error(request, 'Please provide valid Java code.')
                return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
            context = {
                'form': form,
                'recent_predictions': PredictionHistory.objects.all()[:5]
            }
            return render(request, 'home', context)
    
    
    return redirect('home')

# api prediction 
@api_view(['POST'])
def predictApi(request):
      if request.method == 'POST':
          java_code = request.data.get("code", None)
          if not java_code:
               return Response({"error": "No code provided in the request."}, status=400)
          model_path = os.path.join(settings.BASE_DIR, "prediction-files/java-vuln-detection_v2.keras")
          classifier = JavaFunctionClassifier(model_path)
           # Normalizing and prepossing the code
          java_code = remove_java_comments(java_code)
          java_code = allman_to_knr_representation(java_code)
          java_code = create_class_code(java_code)
          java_file_path = os.path.join(settings.BASE_DIR, "api-prediction-files/Sample.java")
          with open(java_file_path, 'w', encoding='utf-8') as out_f:
                                    out_f.write(java_code) 
          method_name = extract_java_method_name(java_code)
          if method_name is None:
               return Response({"error": "Could not extract the method name."}, status=400)
                # Generating AST
          ast_dot_txt_path, ast_success = generate_ast_data(java_file_path)
          if not ast_success:
               return Response({"error": "Error in generating AST"}, status=500)
                #Generating CFG DDG
          cfg_ddg_generation_sucess = generate_cfg_ddg_dot(java_file_path, f"{settings.BASE_DIR}/api-prediction-files/", method_name)
          if not cfg_ddg_generation_sucess:
               return Response({"error": "Error in generating CFG DDG."}, status=500)
                # generating dot txt for CFG,DDG
          cfg_dot_txt_generation_sucess = generate_dot_txt_file(f"{settings.BASE_DIR}/api-prediction-files/cfg/Sample.java.dot", f"{settings.BASE_DIR}/api-prediction-files/cfg/")
          if not cfg_dot_txt_generation_sucess:
               return Response({"error": "Error in generating DOT TXT  CFG."}, status=500)
     
          ddg_dot_txt_generation_sucess = generate_dot_txt_file(f"{settings.BASE_DIR}/api-prediction-files/ddg/Sample.java.dot", f"{settings.BASE_DIR}/api-prediction-files/ddg/")
          if not ddg_dot_txt_generation_sucess:
               return Response({"error": "Error in generating DOT TXT DDG."}, status=500)
                # Building adj matrcices for AST, DDG, CFG
                ## AST
          ast_matrix_path, ast_adj_generation = build_adj_matrix(ast_dot_txt_path, f"{settings.BASE_DIR}/api-prediction-files/npy-files/", "ast", matrix_size=600)
          if not ast_adj_generation:
               return Response({"error": "Error in generating AST adj matrix."}, status=500)
                ## CFG
          cfg_dot_txt_path = f"{settings.BASE_DIR}/api-prediction-files/cfg/Sample.java.dot.txt"
          cfg_matrix_path, cfg_adj_generation = build_adj_matrix(cfg_dot_txt_path, f"{settings.BASE_DIR}/api-prediction-files/npy-files/", "cfg")
          if not cfg_adj_generation:
               return Response({"error": "Error in generating CFG ADJ matrix."}, status=500)
                 ## DDG
          ddg_dot_txt_path = f"{settings.BASE_DIR}/api-prediction-files/ddg/Sample.java.dot.txt"
          ddg_matrix_path, ddg_adj_generation = build_adj_matrix(ddg_dot_txt_path, f"{settings.BASE_DIR}/api-prediction-files/npy-files/", "ddg")
          if not ddg_adj_generation:
               return Response({"error": "Error in generating DDG ADJ matrix."}, status=500)
                # Generating CSS
          css_matrix_path = f"{settings.BASE_DIR}/api-prediction-files/npy-files/css_matrix.npy"
          code_embedding_generation = generate_css(java_file_path, css_matrix_path)
          if not code_embedding_generation:
               return Response({"error": "Error in generating  CSS ."}, status=500)
     
          # Predicting the sample 
          try:
               predictionResult = classifier.predict(ast_matrix_path, cfg_matrix_path, ddg_matrix_path, css_matrix_path)
               return Response({
                    "prediction": predictionResult.upper()
                    })     
          except Exception as e:
                    return Response({
                          "error": f'Error during prediction: {str(e)}'
                    })            

                                
    

        
          
               
                