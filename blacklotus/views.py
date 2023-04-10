from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import IssueForm
from .models import Issue, Comentario
from django.shortcuts import render, redirect
from .forms import IssueForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth import logout
from .forms import RegisterForm,EditProfForm
from django.views import generic
from django.db.models import Q
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.db.models import Q

# Create your views here.

@login_required(login_url='login')
def CreateIssueForm(request):
    return render(request, 'newissue.html')
    
@login_required(login_url='login')
def BulkIssueForm(request):
    return render(request, 'bulkissue.html')

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
def BulkIssue(request):
    if len(request.POST.get("issues")) > 0:
        textarea_input = request.POST['issues']
        lines = textarea_input.split('\n')
        for line in lines:
            sub = line
            des = ""
            type = 1
            severity = 1
            priority = 1
            status = 1
            i = Issue(subject=sub, description=des, creator=request.user.username, status=status, type=type, severity=severity, priority=priority)
            i.save()
    return redirect(showIssues)


@login_required(login_url='login')
def showIssues(request):
    qs = Issue.objects.all().order_by('-creationdate').filter(creator=request.user.username)
    visible = None
    ref = None
    filtrosF = Q()
    filtrosstatus = []
    filtrospriority = []
    filtrostype = []
    filtrosseverity = []
    filtroscreator = []

    if request.method == 'GET':
        if 'r' in request.GET:
            ref = request.GET.get('r')

    if request.method == 'POST':
        if 'clearfiltros' in request.POST:
            filtros = []
            request.session['filtros_status'] = filtros
            request.session['filtros_priority'] = filtros
            request.session['filtros_type'] = filtros
            request.session['filtros_severity'] = filtros
            request.session['filtros_creator'] = filtros
        if 'ocultarfiltros' in request.POST:
            visible = False
        elif 'mostrarfiltros' in request.POST:
            visible = True
        if 'updatefiltros' in request.POST or ('filtros_status' in request.session or 'filtros_creator' in request.session or 'filtros_severity' in request.session or 'filtros_priority' in request.session or 'filtros_type' in request.session):
            if 'filtros_status' not in request.session and 'filtros_creator' not in request.session and 'filtros_severity' not in request.session and 'filtros_priority' not in request.session and 'filtros_type' not in request.session:
                filtrosS = Q()
                filtrosP = Q()
                filtrosT = Q()
                filtrosSv = Q()
                filtrosC = Q()
            else:
                filtrosS = Q()
                filtrosP = Q()
                filtrosT = Q()
                filtrosSv = Q()
                filtrosC = Q()

                if'filtros_status' in request.session:
                    filtrosstatus = request.session["filtros_status"]
                    for filtro in filtrosstatus:
                        filtrosS = Q(status=filtro) | filtrosS

                if 'filtros_priority' in request.session:
                    filtrospriority = request.session["filtros_priority"]
                    for filtro in filtrospriority:
                        filtrosP = Q(priority=filtro) | filtrosP

                if 'filtros_type' in request.session:
                    filtrostype = request.session["filtros_type"]
                    for filtro in filtrostype:
                        filtrosT = Q(type=filtro) | filtrosT

                if 'filtros_severity' in request.session:
                    filtrosseverity = request.session["filtros_severity"]
                    for filtro in filtrosseverity:
                        filtrosSv = Q(severity=filtro) | filtrosSv

                if 'filtros_creator' in request.session:
                    filtroscreator = request.session["filtros_creator"]
                    for filtro in filtroscreator:
                        filtrosC = Q(creator=filtro) | filtrosC


            for filtro in request.POST.getlist("status"):
                filtrosS = Q(status=filtro) | filtrosS
                filtrosstatus.append(filtro)

            for filtro in request.POST.getlist("priority"):
                filtrosP = Q(priority=filtro) | filtrosP
                filtrospriority.append(filtro)

            for filtro in request.POST.getlist("type"):
                filtrosT = Q(type=filtro) | filtrosT
                filtrostype.append(filtro)

            for filtro in request.POST.getlist("severity"):
                filtrosSv = Q(severity=filtro) | filtrosSv
                filtrosseverity.append(filtro)

            for filtro in request.POST.getlist("creator"):
                filtrosC = Q(creator=filtro) | filtrosC
                filtroscreator.append(filtro)

            request.session['filtros_status'] = filtrosstatus
            request.session['filtros_priority'] = filtrospriority
            request.session['filtros_type'] = filtrostype
            request.session['filtros_severity'] = filtrosseverity
            request.session['filtros_creator'] = filtroscreator


            if 'flexRadioInclude' in request.POST:
                filtrosF = filtrosS | filtrosP | filtrosT | filtrosSv | filtrosC
            else:
                filtrosF = filtrosS & filtrosP & filtrosT & filtrosSv & filtrosC
    if ref is not None:
        qs = Issue.objects.filter(filtrosF).order_by('-creationdate').filter(creator=request.user.username).filter(Q(subject__icontains=ref))
    else:
        qs = Issue.objects.filter(filtrosF).order_by('-creationdate').filter(creator=request.user.username)
    return render(request, 'mainIssue.html', {'visible': visible,'qs': qs})
    
       
@login_required(login_url='login')
def BlockIssueForm(request, id):
    if request.method == 'POST':
        if len(request.POST.get("motive")) > 0:
            textarea_input = request.POST['motive']
            request.session['motive'] = textarea_input
            return redirect(SeeIssue, num=id)
    return render(request, 'blockissue.html')


@login_required(login_url='login')
def SeeIssue(request, num):
    if 'bloqued' in request.session:
        bloqued = request.session['bloqued']
        del request.session['bloqued']
    else:
        bloqued = None

    if 'motive' in request.session:
        motive = request.session['motive']
        del request.session['motive']
    else:
        motive = None

    if request.method == 'POST':
        if 'block' in request.POST:
            request.session['bloqued'] = True
            return redirect(BlockIssueForm, id=num)
        elif 'unblock' in request.POST:
            bloqued = False

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

    coment = None
    if request.method == 'GET':
        if 'comment' in request.GET:
            coment = request.GET.get('comment')
            iss = Issue.objects.get(id=num)
            c = Comentario(message=coment, creator=request.user.username, issue = iss)
            c.save()
    coments = Comentario.objects.all().order_by('-creationDate').filter(issue=num)
    return render(request, 'single_issue.html', {'issue': issue, 'bloqued': bloqued, 'motive': motive, 'coments': coments})

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