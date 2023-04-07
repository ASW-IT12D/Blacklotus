
from django.shortcuts import render, redirect
from .forms import IssueForm
from .models import Issue
from django.http import HttpResponse
# Create your views here.

def CreateIssueForm(request):
    return render(request, 'newissue.html')

def CreateIssue(request):
    form = IssueForm(request.POST.copy() or None)
    if form.is_valid():
        form.data['subject'] = "HArd"
        form.save()
    return redirect(showIssues)
def showIssues(request):
    qs = Issue.objects.all().order_by('-creationdate')
    return render(request, 'mainIssue.html', {'qs': qs})


def SeeIssue(request, num):
    issueUpdate = Issue.objects.get(id=num)
    if 'BotonUpdateStatuses' in request.POST:
        if 'status' in request.POST:
            issueUpdate.status = request.POST.get("status")
        if 'severity' in request.POST:
            issueUpdate.severity = request.POST.get("severity")
        if 'type' in request.POST:
                issueUpdate.type = request.POST.get("type")
        issueUpdate.save()
    elif 'EditContent' in request.POST:
        request.session['id'] = num
        return redirect(EditIssue)
    elif 'next' in request.POST:
        try:
            nextIssue = issueUpdate.get_previous_by_creationdate()
            return redirect(SeeIssue,num=nextIssue.id)
        except:
            firstIssue = Issue.objects.order_by('creationdate').last()
            return redirect(SeeIssue, num=firstIssue.id)
    elif 'previous' in request.POST:
        try:
            previousIssue = issueUpdate.get_next_by_creationdate()
            return redirect(SeeIssue,num=previousIssue.id)
        except:
            lastIssue = Issue.objects.order_by('creationdate').first()
            return redirect(SeeIssue, num=lastIssue.id)
    issue = Issue.objects.filter(id=num).values()
    return render(request, 'single_issue.html', {'issue' :issue})

def EditIssue(request):
    ID = request.session.get('id')
    issue = Issue.objects.filter(id=ID).values()
    if 'Update' in request.POST:
        issueUpdate = Issue.objects.get(id=request.POST.get("idHidden"))
        if request.POST.get("subject") is not None and len(request.POST.get("subject")) >0:
            issueUpdate.subject = request.POST.get("subject")
        if request.POST.get("description") is not None and len(request.POST.get("description")) >0:
            issueUpdate.description = request.POST.get("description")
        issueUpdate.save()
        return redirect(SeeIssue,num=request.POST.get("idHidden"))
    else:
        return render(request, 'editIssue.html', {'issue': issue})

def DeleteIssue(request, id):
    issue = Issue.objects.get(id=id)
    issue.delete()
    return redirect(showIssues)

def showFilters(request, filter):

    return render(request ,'mainIssue.html')

def loginPage():
    return None


def signUp():
    return None
