import os
import tempfile
from io import BytesIO

from botocore.exceptions import ClientError
from django.contrib.auth.decorators import login_required
from .models import Issue, Attachments, Activity, Profile
from django.http import HttpResponse

from .models import Issue, Attachments, Activity
from django.shortcuts import render, redirect
from .forms import IssueForm, EditProfileInfoForm
from .models import Issue, Comentario
from django.contrib.auth.models import User

from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from .forms import RegisterForm, IssueForm, AssignedTo, Watchers
from django.views import generic
from django.urls import reverse_lazy
from django.db.models import Q
import boto3
from django.conf import settings
from social_django.utils import psa
from datetime import datetime
import calendar

# Create your views here.

@psa('github')
def github_auth(request):
    # Autenticación de GitHub en segundo plano
    return redirect(showIssues)

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
        i = Issue(subject=sub, description=des, creator=request.user.username, status=status, type=type,
                  severity=severity, priority=priority)
        i.save()
    return redirect(showIssues)


@login_required(login_url='login')
def BulkIssue(request):
    if len(request.POST.get("issues")) > 0:
        textarea_input = request.POST['issues']
        lines = textarea_input.split('\n')
        for line in lines:
            if len(line) > 0:
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
    filtrosasigned = []

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
            request.session['filtros_asignedTo'] = filtros
        if 'ocultarfiltros' in request.POST:
            visible = False
        elif 'mostrarfiltros' in request.POST:
            visible = True
        if 'updatefiltros' in request.POST or ('filtros_status' in request.session or 'filtros_creator' in request.session or 'filtros_asignedTo' in request.session or 'filtros_severity' in request.session or 'filtros_priority' in request.session or 'filtros_type' in request.session):
            if 'filtros_status' not in request.session and 'filtros_asignedTo' not in request.session and 'filtros_creator' not in request.session and 'filtros_severity' not in request.session and 'filtros_priority' not in request.session and 'filtros_type' not in request.session:
                filtrosS = Q()
                filtrosP = Q()
                filtrosT = Q()
                filtrosSv = Q()
                filtrosC = Q()
                filtrosA = Q()

            else:
                filtrosS = Q()
                filtrosP = Q()
                filtrosT = Q()
                filtrosSv = Q()
                filtrosC = Q()
                filtrosA = Q()

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

                if 'filtros_asignedTo' in request.session:
                    filtrosasigned = request.session["filtros_asignedTo"]
                    for filtro in filtrosasigned:
                        if filtro == "Unassigned" or filtro == None:
                            filtrosA = Q(asignedTo=None) | filtrosA
                        else:
                            if isinstance(filtro, int):
                                filtrosA = Q(asignedTo=filtro) | filtrosA
                            else:
                                user = User.objects.get(username=filtro)
                                filtrosA = Q(asignedTo=user.id) | filtrosA


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

            for filtro in request.POST.getlist("assignations"):
                if filtro == "Unassigned" or filtro == None:
                    filtrosA = Q(asignedTo = None)| filtrosA
                    filtrosasigned.append(None)
                else:
                    if isinstance(filtro, int):
                        filtrosA = Q(asignedTo=filtro) | filtrosA
                        filtrosasigned.append(filtro)
                    else:
                        user = User.objects.get(username=filtro)
                        filtrosA = Q(asignedTo=user.id) | filtrosA
                        filtrosasigned.append(user.id)

            request.session['filtros_status'] = filtrosstatus
            request.session['filtros_priority'] = filtrospriority
            request.session['filtros_type'] = filtrostype
            request.session['filtros_severity'] = filtrosseverity
            request.session['filtros_creator'] = filtroscreator
            request.session['filtros_asignedTo'] = filtrosasigned


            if 'flexRadioInclude' in request.POST:
                filtrosF = filtrosS | filtrosP | filtrosT | filtrosSv | filtrosC | filtrosA
            else:
                filtrosF = filtrosS & filtrosP & filtrosT & filtrosSv & filtrosC & filtrosA

    filtroscreator = Q(creator=request.user.username) | Q(asignedTo__username=request.user.username) | Q(watchers__username=request.user.username)
    if ref is not None:
        if sort_by is not None:
            qs = Issue.objects.filter(filtrosF).order_by(sort_by).filter(filtroscreator).filter(
                Q(subject__icontains=ref))
        else:
            qs = Issue.objects.filter(filtrosF).order_by('-creationdate').filter(filtroscreator).filter(
                Q(subject__icontains=ref))
    else:

        if sort_by is not None:
            qs = Issue.objects.filter(filtrosF).order_by(sort_by).filter(filtroscreator)
        else:
            qs = Issue.objects.filter(filtrosF).order_by('-creationdate').filter(filtroscreator)
    allUsers = User.objects.all()
    return render(request, 'mainIssue.html', {'visible': visible,'qs': qs, 'allUsers': allUsers})


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
    form2 = Watchers()
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
                document = Attachments(archivo=archivo, username=request.user.username, issue=issueUpdate)
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
                allAt = Attachments.objects.all().filter(archivo=object_name)
                a = Attachments.objects.all().filter(issue=i, archivo=object_name)
                if (len(allAt) > 1):
                    a.delete()
                elif (len(allAt) == 1):
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
        elif 'BotonUpdateWatchers' in request.POST:
            formW = Watchers(request.POST)
            if formW.is_valid():
                names = formW.cleaned_data['watchers']
                aux = Issue.objects.get(id=num)
                listUsernames = list(names.values_list('username', flat=True))
                auxU = User.objects.filter(username__in=listUsernames)
                aux.watchers.set(auxU)
                aux.save()

        elif 'deadline' in request.POST:
            return redirect(deadLineForm, id=num)
        elif 'deldeadline' in request.POST:

            issueUpdate.deadline = False
            issueUpdate.deadlinemotive = ""
            issueUpdate.save()
    issueUpdate = Issue.objects.get(id=num)
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
            return redirect(SeeIssue, num=nextIssue.id)
        except:
            firstIssue = Issue.objects.order_by('creationdate').last()
            return redirect(SeeIssue, num=firstIssue.id)
    elif 'previous' in request.POST:
        try:
            previousIssue = issueUpdate.get_next_by_creationdate()
            return redirect(SeeIssue, num=previousIssue.id)
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
            if len(coment) > 0:
                iss = Issue.objects.get(id=num)
                user = User.objects.get(username=request.user.username)
                c = Comentario(message=coment, creator=user, issue=iss)
                c.save()
    coments = Comentario.objects.all().order_by('-creationDate').filter(issue=num)


    images = {}
    for c in coments:
        creator = User.objects.get(id=c.creator_id)
        profileUserc = Profile.objects.get(user=creator)
        imageUserc = profileUserc.get_url_image()
        images[c] = imageUserc

    instance = Issue.objects.get(id=num)
    asignedTo = instance.asignedTo.all()
    user = User.objects.get(username=request.user.username)
    profile = Profile.objects.get(user=user)
    image_url = profile.get_url_image()
    watchers = instance.watchers.all()
    return render(request, 'single_issue.html',
                  {'image_url': image_url, 'issue': issue, 'form': form, 'form2': form2,
                   'asignedTo': asignedTo, 'coments': coments, 'activity': activity, 'commentsOn': commentsOn,
                   'documents': documents, 'watchers': watchers,'images': images})

@login_required(login_url='login')
def EditIssue(request):
    ID = request.session.get('id')
    issue = Issue.objects.filter(id=ID).values()
    if 'Update' in request.POST:
        user = request.user.username
        issueUpdate = Issue.objects.get(id=request.POST.get("idHidden"))
        if request.POST.get("subject") is not None and len(request.POST.get("subject")) > 0:
            field = "subject"
            old = issueUpdate.getSubject()
            new = request.POST.get("subject")
            act = Activity(field=field, change=new, old=old, user=user, issueChanged=issueUpdate)
            act.save()
            issueUpdate.subject = request.POST.get("subject")
        if request.POST.get("description") is not None and len(request.POST.get("description")) > 0:
            field = "description"
            old = issueUpdate.getDescription()
            new = request.POST.get("description")
            act = Activity(field=field, change=new, old=old, user=user, issueChanged=issueUpdate)
            act.save()
            issueUpdate.description = request.POST.get("description")
        issueUpdate.save()
        return redirect(SeeIssue, num=request.POST.get("idHidden"))
    else:
        return render(request, 'editIssue.html', {'issue': issue})


@login_required(login_url='login')
def DeleteIssue(request, id):
    issue = Issue.objects.get(id=id)
    issue.delete()
    return redirect(showIssues)


def log(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect(showIssues)
    else:
        form = AuthenticationForm()
    return render(request, 'loginPage.html', {'form': form})


def join(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(log)
    else:
        form = RegisterForm()
    return render(request, 'signUp.html', {'form': form})


@login_required
def custom_logout(request):
    logout(request)
    return redirect('home')


@login_required
def showProfile(request):
    user = User.objects.get(username=request.user.username)
    profile = Profile.objects.get(user=user)
    image_url = profile.get_url_image()
    return render(request, 'viewProfile.html', {'image_url':image_url})


def redirectLogin(request):
    return redirect(log)


class ProfileEditView(generic.UpdateView):
    form_class = EditProfileInfoForm
    template_name = 'editUser.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

@login_required(login_url='login')
def deadLineForm(request, id):
    current_year = datetime.now().year

    days = [str(day) for day in range (1, 32)]
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    years = [str(year) for year in range (current_year, current_year + 10)]

    months_dict = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                   'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}

    context = {
        'days': days,
        'months': months,
        'years': years,
    }

    issue = Issue.objects.get(id=id)

    if request.method == 'POST':
        day = int(request.POST['day'])
        month = request.POST['month']
        year = int(request.POST['year'])

        try:
            deadline_date = datetime.strptime(f"{day} {month} {year}", "%d %B %Y")
        except ValueError:
            return render(request, 'newDeadLine.html', context)

        now = datetime.now()
        last_day = calendar.monthrange(year, months_dict[month])[1]

        if deadline_date < now or day > last_day:
            return render(request, 'newDeadLine.html', context)


        issue.deadlinedate = deadline_date
        issue.deadline = True

        if len(request.POST.get("motive")) > 0:
            textarea_input = request.POST['motive']
            issue.deadlinemotive = textarea_input

        issue.save()

        return redirect(SeeIssue, num=id)

    return render(request, 'newDeadLine.html', context)


