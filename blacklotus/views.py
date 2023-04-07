

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Issue
from django.shortcuts import render, redirect
from .forms import IssueForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth import logout
from .forms import RegisterForm,EditProfForm
from django.views import generic
from django.urls import reverse_lazy
@login_required(login_url='login')
def CreateIssueForm(request):
    return render(request, 'newissue.html')

@login_required(login_url='login')
def CreateIssue(request):
    if len(request.POST.get("subject")) > 0:
        sub = request.POST.get("subject")
        des = request.POST.get("description")
        type = request.POST.get("type")
        severity = request.POST.get("severity")
        priority = request.POST.get("priority")
        status = request.POST.get("status")
        i = Issue(subject=sub, description=des, creator=request.user.username, status=status, type=type, severity=severity, priority=priority)
        i.save()
    return redirect(showIssues)
@login_required(login_url='login')
def showIssues(request):
    qs = Issue.objects.all().order_by('-creationdate').filter(creator=request.user.username)
    return render(request, 'mainIssue.html', {'qs': qs})

@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
def DeleteIssue(request, id):
    issue = Issue.objects.get(id=id)
    issue.delete()
    return redirect(showIssues)

@login_required(login_url='login')
def showFilters(request):
    visible = False
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
            return redirect(showIssues)
    else:
        form = AuthenticationForm()
    return render(request, 'loginPage.html',{'form': form})


def join(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(log)
    else:
        form = RegisterForm()
    return render(request, 'signUp.html',{'form': form})

@login_required
def custom_logout(request):
    logout(request)
    return redirect('home')

@login_required
def showProfile(request):
    return render(request, 'viewProfile.html')

def redirectLogin(request):
    return redirect(log)

class UserEditView(generic.UpdateView):
    form_class = EditProfForm
    template_name = 'editProfile.html'
    success_url = reverse_lazy('home')
    def get_object(self):
        return self.request.user