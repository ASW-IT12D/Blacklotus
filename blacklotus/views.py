

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

    i = Issue(subject=sub, description=des,creator="Llus",status=status,type=type,severity=severity,priority=priority)
    i.save()
    return redirect(showIssues)
def showIssues(request):
    qs = Issue.objects.all
    return render(request, 'mainIssue.html', {'qs': qs})