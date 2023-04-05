from django import forms
from .models import Issue
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['subject', 'status', 'description', 'type', 'severity', 'priority']


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username','fullName', 'email', 'password1', 'password2']
