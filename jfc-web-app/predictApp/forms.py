from django import forms

class JavaCodeForm(forms.Form):
    java_code = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 15,
            'placeholder': 'Enter your Java function here...'
        }),
        label='Java Function Code',
        required=False
    )
    
    java_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.java,.txt'
        }),
        label='Or upload a Java file',
        required=False
    )
    
    def clean(self):
        cleaned_data = super().clean()
        java_code = cleaned_data.get('java_code')
        java_file = cleaned_data.get('java_file')
        
        if not java_code and not java_file:
            raise forms.ValidationError("Please provide either Java code or upload a file.")
        
        if java_file:
            # Validate file extension
            if not java_file.name.lower().endswith(('.java', '.txt')):
                raise forms.ValidationError("Please upload a .java or .txt file.")
            
            # Validate file size (5MB max)
            if java_file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size must be less than 5MB.")
        
        return cleaned_data