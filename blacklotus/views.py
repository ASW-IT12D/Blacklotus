

from django.shortcuts import render, redirect

from .models import Issue
from django.http import HttpResponse
# Create your views here.

def CreateIssueForm(request):
    return render(request, 'newissue.html')

def CreateIssue(request):
    sub = request.POST.get("subject")
    des = request.POST.get("description")
    type = request.POST.get("type")
    severity = request.POST.get("severity")
    priority = request.POST.get("priority")
    status = request.POST.get("status")

    i = Issue(subject=sub, description=des,creator="Lluis",status=status,type=type,severity=severity,priority=priority)
    i.save()
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

