from django import forms
from .models import JobCSVImport, Job

class JobCSVImportForm(forms.ModelForm):
    class Meta:
        model = JobCSVImport
        fields = ['file']

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = '__all__'
      