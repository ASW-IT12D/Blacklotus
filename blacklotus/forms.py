from django import forms
from .models import Issue,Profile
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.auth.models import User


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['subject', 'status', 'description', 'type', 'severity', 'priority']

class RegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class' : 'form-control'}))
    first_name = forms.CharField(max_length=80,widget=forms.TextInput(attrs={'class' : 'form-control'}))
    class Meta:
        model = User
        fields = ['username','first_name','email','password1','password2']



class EditProfileInfoForm(forms.ModelForm):
    username = forms.CharField(max_length=80, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class' : 'form-control'}))
    first_name = forms.CharField(max_length=80,widget=forms.TextInput(attrs={'class' : 'form-control'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 7, 'placeholder': 'Optional'}), required=False)
    image = forms.ImageField(required=False, widget=forms.FileInput(
        attrs={'class': 'form-control-file', 'id': 'archivo', 'name': 'archivo'}))
    class Meta:
        model = Profile
        fields = ['username','email','first_name','bio', 'image']

    def save(self, commit=True):
        user = super(EditProfileInfoForm,self).save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.save()
        profile = user.profile
        profile.bio = self.cleaned_data['bio']
        profile.image = self.cleaned_data['image']
        profile.save()

        return profile
class AssignedTo(forms.ModelForm):
    asignedTo = forms.ModelMultipleChoiceField(queryset=User.objects.all(), to_field_name='username')
    class Meta:
        model = Issue
        fields = ['asignedTo']

class Watchers(forms.ModelForm):
    watchers = forms.ModelMultipleChoiceField(queryset=User.objects.all(), to_field_name='username')
    class Meta:
        model = Issue
        fields = ['watchers']
