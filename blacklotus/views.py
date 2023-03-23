from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def CreateIssue(request):
    return render(request, 'newissue.html', {'name': 'Marc'})

def showIssues(request):
    return render(request, 'newissue.html', {'name': 'Marc'})