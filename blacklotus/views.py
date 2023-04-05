from .models import Issue
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
def CreateIssueForm(request):
    return render(request, 'newissue.html')

def CreateIssue(request):
    sub = request.POST.get("subject")
    des = request.POST.get("description")
    type = request.POST.get("type")
    severity = request.POST.get("severity")
    priority = request.POST.get("priority")
    status = request.POST.get("status")
    i = Issue(subject=sub, description=des, creator="Llus", status=status, type=type, severity=severity, priority=priority)
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

def log(request):
    if request.method == 'POST':
        form = AuthenticationForm(request,data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            return redirect('home')
        else:
            print(form.errors)
            return render(request,'failedLogin.html')
    else:
        form = AuthenticationForm()
    return render(request, 'loginPage.html', {'form': form})

def join(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(log)
    else:
        form = UserCreationForm()
    return render(request, 'signUp.html',{'form': form})