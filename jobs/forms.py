from django import forms
from .models import JobCSVImport, Job


class JobCSVImportForm(forms.ModelForm):
    class Meta:
        model = JobCSVImport
        fields = ["file"]
        widgets = {
            "file": forms.FileInput(attrs={
                "class": "form-control"
            })
        }


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = "__all__"
        widgets = {
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 8,
                "placeholder": "Write detailed job description..."
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply Bootstrap class to all fields
        for name, field in self.fields.items():

            if name != "description":
                field.widget.attrs.update({
                    "class": "form-control"
                })