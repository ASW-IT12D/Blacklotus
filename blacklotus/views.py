import os
import tempfile
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .models import Issue, Attachments, Activity
from django.shortcuts import render, redirect
from .forms import IssueForm
from .models import Issue, Comentario
from .models import Issue
from django.contrib.auth.models import User

from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from .forms import RegisterForm,EditProfForm,IssueForm,AssignedTo
from django.views import generic
from django.urls import reverse_lazy
from django.db.models import Q
import boto3
from django.conf import settings

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

    sort_by = None
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
        if 'sort' in request.GET:
            sort_by = request.GET.get('sort')
            order = request.GET.get('direction')
            if order == 'desc':
                sort_by = '-' + sort_by

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
        if sort_by is not None:
            qs = Issue.objects.filter(filtrosF).order_by(sort_by).filter(creator=request.user.username).filter(Q(subject__icontains=ref))
        else:
            qs = Issue.objects.filter(filtrosF).order_by('-creationdate').filter(creator=request.user.username).filter(Q(subject__icontains=ref))
    else:
        if sort_by is not None:
            qs = Issue.objects.filter(filtrosF).order_by(sort_by).filter(creator=request.user.username)
        else:
            qs = Issue.objects.filter(filtrosF).order_by('-creationdate').filter(creator=request.user.username)
    return render(request, 'mainIssue.html', {'visible': visible,'qs': qs})


@login_required(login_url='login')
def BlockIssueForm(request, id):
    if request.method == 'POST':
        if len(request.POST.get("motive")) > 0:
            issueUpdate = Issue.objects.get(id=id)
            issueUpdate.blockmotive = request.POST['motive']
            issueUpdate.save()
            return redirect(SeeIssue, num=id)
    return render(request, 'blockissue.html')

def list_documents(num):
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      aws_session_token=settings.AWS_SESSION_TOKEN)
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    prefix = 'Attachments/'
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    documents = []
    for content in response.get('Contents', []):
        if content.get("Key") != 'Attachments/':
            i = Issue.objects.get(id=num)
            a = Attachments.objects.all().filter(issue=i, archivo=content.get("Key"))
            if (len(a) > 0):
                url = f"{content['Key']}"
                url = url.replace("Attachments/", "")
                documents.append(url)
    return documents

@login_required(login_url='login')
def SeeIssue(request, num):
    form = AssignedTo()
    if 'commentsOn' in request.session:
        commentsOn = request.session['commentsOn']
    else:
        commentsOn = True

    if request.method == "POST":
        if 'comments' in request.POST:
            request.session['commentsOn'] = True
            commentsOn = True
        elif 'activity' in request.POST:
            request.session['commentsOn'] = False
            commentsOn = False
        if 'archivo' in request.FILES and request.FILES['archivo']:
            archivo = request.FILES.get('archivo')
            if len(archivo) > 0:
                issueUpdate = Issue.objects.get(id=num)
                document = Attachments(archivo=archivo,username=request.user.username,issue=issueUpdate)
                document.save()
        elif 'Download' in request.POST:
            option_selected = request.POST.get('option')
            if option_selected is not None:
                s3 = boto3.client('s3',
                                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                  aws_session_token=settings.AWS_SESSION_TOKEN)

                object_name = 'Attachments/' + option_selected
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    s3.download_file(settings.AWS_STORAGE_BUCKET_NAME, object_name, temp_file.name)
                with open(temp_file.name, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/octet-stream')
                    response['Content-Disposition'] = 'attachment; filename="{}"'.format(option_selected)
                return response

        elif 'Delete' in request.POST:
            option_selected = request.POST.get('option')
            if option_selected is not None:
                s3 = boto3.client('s3',
                                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                  aws_session_token=settings.AWS_SESSION_TOKEN)
                object_name = 'Attachments/' + option_selected
                i = Issue.objects.get(id=num)
                a = Attachments.objects.all().filter(issue=i, archivo=object_name)
                if (len(a) > 1):
                    a.delete()
                elif (len(a)==1):
                    a.delete()
                    response = s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=object_name)
    documents = list_documents(num)

    issueUpdate = Issue.objects.get(id=num)

    if request.method == 'POST':
        if 'block' in request.POST:
            issueUpdate.blocked = True
            issueUpdate.save()
            return redirect(BlockIssueForm, id=num)
        elif 'unblock' in request.POST:
            issueUpdate.blocked = False
            issueUpdate.blockmotive = ""
            issueUpdate.save()
        elif 'BotonUpdateAsign' in request.POST:
            formN = AssignedTo(request.POST)
            if formN.is_valid():
                names = formN.cleaned_data['asignedTo']
                aux = Issue.objects.get(id=num)
                listUsernames = list(names.values_list('username', flat=True))
                auxU = User.objects.filter(username__in=listUsernames)
                aux.asignedTo.set(auxU)
                aux.save()

    if 'BotonUpdateStatuses' in request.POST:
        user = request.user.username
        if 'status' in request.POST:
            field = "status"
            old = issueUpdate.getStatus()
            new = request.POST.get("status")
            act = Activity(field=field, change=new, old=old, user=user, issueChanged=issueUpdate)
            act.save()
            issueUpdate.status = request.POST.get("status")
        if 'severity' in request.POST:
            field = "severity"
            old = issueUpdate.getStatus()
            new = request.POST.get("severity")
            act = Activity(field=field, change=new, old=old, user=user, issueChanged=issueUpdate)
            act.save()
            issueUpdate.severity = request.POST.get("severity")
        if 'type' in request.POST:
            field = "type"
            old = issueUpdate.getStatus()
            new = request.POST.get("type")
            act = Activity(field=field, change=new, old=old, user=user, issueChanged=issueUpdate)
            act.save()
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
    issueAct = Issue.objects.get(id=num)
    activity = Activity.objects.filter(issueChanged=issueAct).order_by('-creationdate').values()
    coment = None
    if request.method == 'GET':
        if 'comment' in request.GET:
            coment = request.GET.get('comment')
            iss = Issue.objects.get(id=num)
            c = Comentario(message=coment, creator=request.user.username, issue = iss)
            c.save()
    coments = Comentario.objects.all().order_by('-creationDate').filter(issue=num)

    instance = Issue.objects.get(id=num)
    asignedTo = instance.asignedTo.all()
    return render(request, 'single_issue.html', {'issue':issue,'form':form,'asignedTo':asignedTo, 'coments': coments, 'activity':activity, 'commentsOn': commentsOn,'documents':documents})


@login_required(login_url='login')
def EditIssue(request):
    ID = request.session.get('id')
    issue = Issue.objects.filter(id=ID).values()
    if 'Update' in request.POST:
        user = request.user.username
        issueUpdate = Issue.objects.get(id=request.POST.get("idHidden"))
        if request.POST.get("subject") is not None and len(request.POST.get("subject")) >0:
            field = "subject"
            old = issueUpdate.getSubject()
            new = request.POST.get("subject")
            act = Activity(field=field, change=new,old=old,user=user, issueChanged=issueUpdate)
            act.save()
            issueUpdate.subject = request.POST.get("subject")
        if request.POST.get("description") is not None and len(request.POST.get("description")) >0:
            field = "description"
            old = issueUpdate.getDescription()
            new = request.POST.get("description")
            act = Activity(field=field, change=new, old=old, user=user, issueChanged=issueUpdate)
            act.save()
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

