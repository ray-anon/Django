from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from .forms import DocumentForm
from .models import Document
import pandas as pd

def upload_file(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save()
            file_path = document.file.path

            try:
                # Read the uploaded file
                if file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path)
                else:
                    df = pd.read_csv(file_path)
                
                # Check if required columns exist
                required_columns = ['Cust State', 'DPD']
                if not all(column in df.columns for column in required_columns):
                    raise ValidationError("Uploaded file must contain 'Cust State' and 'DPD' columns")

                # Generate summary report
                summary_df = df.groupby(['Cust State', 'DPD']).size().reset_index(name='Count')
                summary_html = summary_df.to_html(index=False)

                return render(request, 'summary.html', {'summary': summary_html})
            
            except Exception as e:
                return render(request, 'upload.html', {'form': form, 'error': str(e)})
        
    else:
        form = DocumentForm()
    return render(request, 'upload.html', {'form': form})
