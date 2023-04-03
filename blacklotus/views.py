

from django.shortcuts import render, redirect
from .forms import IssueForm
from .models import Issue
from django.http import HttpResponse
# Create your views here.

def CreateIssueForm(request):
    return render(request, 'newissue.html')

def CreateIssue(request):
    form = IssueForm(request.POST or None)
    if form.is_valid():
        form.save()
    return redirect(showIssues)
def showIssues(request):
    qs = Issue.objects.all().order_by('-creationdate')
    return render(request, 'mainIssue.html', {'qs': qs})

def SeeIssue(request, num):
    issue = Issue.objects.filter(id=num).values()
    return render(request, 'single_issue.html', {'issue':issue})

def DeleteIssue(request, id):
    issue = Issue.objects.get(id=id)
    issue.delete()
    return redirect(showIssues)

def showFilters(request):
    visible = False;
    if request.method == 'POST':
        if 'togglefiltros' in request.POST:
            visible = not visible
    return render(request,'mainIssue.html', {'visible': visible})

def loginPage():
    return None


def signUp():
    return None