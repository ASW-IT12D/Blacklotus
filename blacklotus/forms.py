from django import forms
from .models import Issue
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.auth.models import User


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['subject', 'status', 'description', 'type', 'severity', 'priority']

class RegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class' : 'form-control'}))
    first_name = forms.CharField(max_length=80,widget=forms.TextInput(attrs={'class' : 'form-control'}))
    second_name = forms.CharField(max_length=80,widget=forms.TextInput(attrs={'class' : 'form-control'}))
    class Meta:
        model = User
        fields = ['username','first_name','second_name','email','password1','password2']

class EditProfForm(UserChangeForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class' : 'form-control'}))
    first_name = forms.CharField(max_length=80,widget=forms.TextInput(attrs={'class' : 'form-control'}))
    second_name = forms.CharField(max_length=80,widget=forms.TextInput(attrs={'class' : 'form-control'}))
    class Meta:
        model = User
        fields = ['username','first_name','second_name','email']