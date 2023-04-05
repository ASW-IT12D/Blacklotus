from django import forms
from .models import Issue



class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['subject', 'status', 'description', 'type', 'severity', 'priority']


