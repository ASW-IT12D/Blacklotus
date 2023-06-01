import calendar
import json
import tempfile
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from social_django.utils import psa

from .forms import EditProfileInfoForm, RegisterForm, AssignedTo, Watchers
from .models import Attachments, Activity, Issue, Comentario, Profile
from .serializers import IssueSerializer, ActivitySerializer, ProfileSerializer, IssuesSerializer, \
    AttachmentsSerializer, CommentsSerializer


# Create your views here.

@psa('github')
def github_auth(request):
    # Autenticación de GitHub en segundo plano
    return redirect(showIssues)

@login_required(login_url='login')
def CreateIssueForm(request):
    if request.method == 'POST':
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
    else:
        return render(request, 'newissue.html')

@login_required(login_url='login')
def BulkIssueForm(request):
    if request.method == "POST":
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
                    i = Issue(subject=sub, description=des, creator=request.user.username, status=status, type=type,
                              severity=severity, priority=priority)
                    i.save()
        return redirect(showIssues)
    return render(request, 'bulkissue.html')

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
        if 'updatefiltros' in request.POST or (
                'filtros_status' in request.session or 'filtros_creator' in request.session or 'filtros_asignedTo' in request.session or 'filtros_severity' in request.session or 'filtros_priority' in request.session or 'filtros_type' in request.session):
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

                if 'filtros_status' in request.session:
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
                    filtrosA = Q(asignedTo=None) | filtrosA
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

    filtroscreator = Q(creator=request.user.username) | Q(asignedTo__username=request.user.username) | Q(
        watchers__username=request.user.username)
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
    return render(request, 'mainIssue.html', {'visible': visible, 'qs': qs, 'allUsers': allUsers})

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
    try:
        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        prefix = 'Attachments/'
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        documents = []
        for content in response.get('Contents', []):
            i = Issue.objects.get(id=num)
            nombre = content.get("Key").replace("Attachments/", "")
            a = Attachments.objects.all().filter(issue=i, archivo=nombre)
            if (len(a) > 0):
                url = f"{content['Key']}"
                url = url.replace("Attachments/", "")
                documents.append(url)
        return documents
    except ClientError as e:
        print(e)
        documents = []
        return documents

@login_required(login_url='login')
def SeeIssue(request, num):
    form = AssignedTo()
    form2 = Watchers()

    issueUpdate = Issue.objects.get(id=num)

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
            file_name = archivo.name
            file = Attachments.objects.filter(archivo=file_name)
            if len(archivo) > 0 and len(file) == 0:
                document = Attachments(archivo=archivo, username=request.user.username, issue=issueUpdate)
                document.save()
        elif 'Download' in request.POST:
            option_selected = request.POST.get('option')
            if option_selected is not None:
                try:
                    s3 = boto3.client('s3',
                                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
                    object_name = 'Attachments/' + option_selected
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        s3.download_file(settings.AWS_STORAGE_BUCKET_NAME, object_name, temp_file.name)
                    with open(temp_file.name, 'rb') as f:
                        response = HttpResponse(f.read(), content_type='application/octet-stream')
                        response['Content-Disposition'] = 'attachment; filename="{}"'.format(option_selected)
                    return response
                except ClientError as e:
                    print(e)
        elif 'Delete' in request.POST:
            option_selected = request.POST.get('option')
            if option_selected is not None:
                try:
                    s3 = boto3.client('s3',
                                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
                    object_name = 'Attachments/' + option_selected
                    i = Issue.objects.get(id=num)
                    allAt = Attachments.objects.all().filter(archivo=object_name)
                    a = Attachments.objects.all().filter(issue=i, archivo=object_name)
                    if (len(allAt) > 1):
                        a.delete()
                    elif (len(allAt) == 1):
                        a.delete()
                        s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=object_name)
                except ClientError as e:
                    print(e)
        elif 'block' in request.POST:
            issueUpdate.blocked = True
            issueUpdate.save()
            return redirect(BlockIssueForm, id=num)
        elif request.POST.get('_method') == 'DELETE':
            issue = Issue.objects.get(id=num)
            issue.delete()
            return redirect(showIssues)
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
            action = request.POST.get('BotonUpdateWatchers')
            if (action == 'add'):
                formW = Watchers(request.POST)
                if formW.is_valid():
                    names = formW.cleaned_data['watchers']
                    aux = Issue.objects.get(id=num)
                    listUsernames = list(names.values_list('username', flat=True))
                    users = aux.watchers.all()
                    for u in users:
                        listUsernames.append(u.username)
                    auxU = User.objects.filter(username__in=listUsernames)
                    aux.watchers.set(auxU)
                    aux.save()
            else:
                formW = Watchers(request.POST)
                if formW.is_valid():
                    names = formW.cleaned_data['watchers']
                    listUsernames = list(names.values_list('username', flat=True))
                    users = User.objects.filter(username__in=listUsernames)
                    aux = Issue.objects.get(id=num)
                    aux.watchers.remove(*users)
                    aux.save()
        elif 'deadline' in request.POST:
            return redirect(deadLineForm, id=num)
        elif 'deldeadline' in request.POST:
            issueUpdate.deadline = False
            issueUpdate.deadlinemotive = ""
            issueUpdate.save()
        elif 'BotonUpdateStatuses' in request.POST:
            user = request.user
            if 'status' in request.POST:
                field = "status"
                old = issueUpdate.getStatus()
                new = request.POST.get("status")
                act = Activity(field=field, change=new, old=old, user=user, issueChanged=issueUpdate)
                act.save()
                issueUpdate.status = request.POST.get("status")
            if 'severity' in request.POST:
                field = "severity"
                old = issueUpdate.getSeverity()
                new = request.POST.get("severity")
                act = Activity(field=field, change=new, old=old, user=user, issueChanged=issueUpdate)
                act.save()
                issueUpdate.severity = request.POST.get("severity")
            if 'type' in request.POST:
                field = "type"
                old = issueUpdate.getType()
                new = request.POST.get("type")
                act = Activity(field=field, change=new, old=old, user=user, issueChanged=issueUpdate)
                act.save()
                issueUpdate.type = request.POST.get("type")
            if 'priority' in request.POST:
                field = "priority"
                old = issueUpdate.getPriority()
                new = request.POST.get("priority")
                act = Activity(field=field, change=new, old=old, user=user, issueChanged=issueUpdate)
                act.save()
                issueUpdate.priority = request.POST.get("priority")
            issueUpdate.save()
        elif 'EditContent' in request.POST:
            request.session['id'] = num
            return redirect(EditIssue, num)
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

    imagesC = {}
    for c in coments:
        creator = User.objects.get(id=c.creator_id)
        profileUserc = Profile.objects.get(user=creator)
        imageUserc = profileUserc.get_url_image()
        imagesC[c] = imageUserc

    activity = Activity.objects.all().filter(issueChanged=issueAct).order_by('-creationdate')
    imagesA = {}
    for c in activity:
        creator = User.objects.get(id=c.user_id)
        profileUserc = Profile.objects.get(user=creator)
        imageUserc = profileUserc.get_url_image()
        imagesA[c] = imageUserc

    instance = Issue.objects.get(id=num)
    asignedTo = instance.asignedTo.all()
    user = User.objects.get(username=request.user.username)
    profile = Profile.objects.get(user=user)
    image_url = profile.get_url_image()
    watchers = instance.watchers.all()
    documents = list_documents(num)
    return render(request, 'single_issue.html',
                  {'image_url': image_url, 'issue': issue, 'form': form, 'form2': form2,
                   'asignedTo': asignedTo, 'coments': coments, 'activity': activity, 'commentsOn': commentsOn,
                   'documents': documents, 'watchers': watchers, 'imagesC': imagesC, 'imagesA': imagesA})

@login_required(login_url='login')
def EditIssue(request, id):
    ID = request.session.get('id')
    issue = Issue.objects.filter(id=ID).values()
    if 'Update' in request.POST:
        user = request.user
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
def showProfile(request, usernameProf):
    user = User.objects.get(username=usernameProf)
    profile = Profile.objects.get(user=user)
    image_url = profile.get_url_image()
    timeline = Activity.objects.all().filter(user=user).order_by('-creationdate')
    watchers = Issue.objects.all().filter(watchers=user)
    timelineOn = True
    if request.method == "POST":
        if 'timeline' in request.POST:
            timelineOn = True
        elif 'watched' in request.POST:
            timelineOn = False
    return render(request, 'viewProfile.html',
                  {'image_url': image_url, 'profile': profile, 'timeline': timeline, 'watchers': watchers,
                   'timelineOn': timelineOn})

def showProfileRedir(request):
    return redirect(showProfile, request.user.username)

def redirectLogin(request):
    return redirect(log)

class ProfileEditView(generic.UpdateView):
    form_class = EditProfileInfoForm
    template_name = 'editUser.html'
    success_url = reverse_lazy('profileR')

    def get_object(self):
        return self.request.user

@login_required(login_url='login')
def deadLineForm(request, id):
    current_year = datetime.now().year

    days = [str(day) for day in range(1, 32)]
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    years = [str(year) for year in range(current_year, current_year + 10)]

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

def get_token(request):
    # Definimos la URL de la API de autenticación
    token, created = Token.objects.get_or_create(user=request.user)

    # Aquí puedes hacer lo que necesites con el token, por ejemplo guardarlo en una variable o en una sesión
    return render(request, 'token.html', {'token': token.key})

class IssueAPIView(APIView):
    serializer_class = IssueSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        try:
            tieneAcceso = check_user(id, request.auth.user)
            if tieneAcceso:
                issue = Issue.objects.get(id=id)
                issue_serializer = self.serializer_class(issue)
                response_data = {
                    'data': issue_serializer.data
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({'message': "You don't have permission to edit this Issue"},
                                status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response({'message': 'No issues found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id):
        try:
            issue = Issue.objects.get(id=id)
            tieneAcceso = check_user(id, request.auth.user)
            if tieneAcceso:
                data = json.loads(request.body)
                if ('subject' in data):
                    subject = data.get('subject')
                else:
                    subject = None
                if ('description' in data):
                    description = data.get('description')
                else:
                    description = None
                if ('status' in data):
                    statuses = data.get('status')
                    if not check_in(statuses, "status"):
                        return Response({'message': 'status edited successfully'}, status=status.HTTP_200_OK)
                else:
                    statuses = None
                if ('type' in data):
                    type = data.get('type')
                    if not check_in(type, "type"):
                        return Response({'message': 'type edited successfully'}, status=status.HTTP_200_OK)
                else:
                    type = None

                if ('severity' in data):
                    severity = data.get('severity')
                    if not check_in(severity, "severity"):
                        return Response({'message': 'severity edited successfully'}, status=status.HTTP_200_OK)
                else:
                    severity = None

                if ('priority' in data):
                    priority = data.get('priority')
                    if not check_in(priority, "priority"):
                        return Response({'message': 'priority edited successfully'}, status=status.HTTP_200_OK)
                else:
                    priority = None

                if ('blocked' in data):
                    if data.get('blocked') == False:
                        issue.blocked = False
                        issue.blockmotive = ""
                        issue.save()
                    else:
                        if ('blocked_motive' in data):
                            motive = data.get('blocked_motive')
                            if len(motive) > 0:
                                issue.blockmotive = motive
                                issue.blocked = True
                                issue.save()
                            else:
                                return Response({'message': 'Block motive was not included'},
                                                status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({'message': 'Block motive was not included'},
                                            status=status.HTTP_400_BAD_REQUEST)

                if ('deadline' in data):
                    if data.get('deadline') == False:
                        issue.deadline = False
                        issue.deadlinemotive = ""
                        issue.deadlinedate = None

                        issue.save()
                    else:
                        if ('deadline_date' in data):
                            deadline_str = data.get('deadline_date')
                            try:
                                deadline = datetime.strptime(deadline_str, "%d-%m-%Y")
                            except:
                                return Response({'message': 'Invalid deadline format, it should be dd-mm-yyyy'},
                                                status=status.HTTP_406_NOT_ACCEPTABLE)

                            now = datetime.now()
                            last_day = calendar.monthrange(deadline.year, deadline.month)[1]

                            if deadline < now or deadline.day > last_day:
                                return Response(
                                    {'message': 'Invalid deadline format, date can not be earlier than today'},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)

                            issue.deadlinedate = deadline

                        else:
                            return Response({'message': 'Deadline was not included'},
                                            status=status.HTTP_400_BAD_REQUEST)

                        if ('deadline_motive' in data):
                            motive = data.get('deadline_motive')
                            if len(motive) > 0:
                                issue.deadlinemotive = motive
                        issue.deadline = True
                        issue.save()
                if ('watchers' in data):
                    user_str = data.get('watchers')
                    user = User.objects.get(username=user_str)
                    issue.watchers.add(user)
                if ('asignTo' in data):
                    user_str = data.get('asignTo')
                    user = User.objects.get(username=user_str)
                    issue.asignedTo.add(user)
                if (subject != None):
                    issue.subject = subject
                if (description != None):
                    issue.description = description
                if (statuses != None):
                    statusesNum = traduce(statuses, "status")
                    issue.status = statusesNum
                if (type != None):
                    typeNum = traduce(type, "type")
                    issue.type = typeNum
                if (severity != None):
                    severityNum = traduce(severity, "severity")
                    issue.severity = severityNum
                if (priority != None):
                    priorityNum = traduce(priority, "priority")
                    issue.priority = priorityNum
                issue.save()

                return Response({'message': 'Issue edited successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': "You don't have permission to edit this Issue"},
                                status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            try:
                Issue.objects.get(id=id)
                return Response({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                return Response({'message': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        try:
            issue = Issue.objects.get(id=id)
            user = User.objects.get(username=request.auth.user)
            tieneAcceso = check_user(id, request.auth.user)
            if tieneAcceso:
                issue.delete()
                return Response({'Issue deleted'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': "You don't have permission to edit this Issue"},
                                status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response({'Error: Issue does not exist'}, status=status.HTTP_404_NOT_FOUND)

class IssuesAPIView(APIView):
    serializer_class = IssuesSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            filtrosS = Q()
            filtrosP = Q()
            filtrosT = Q()
            filtrosSv = Q()
            filtrosC = Q()
            filtrosA = Q()
            filtrosN = Q()
            filtrosSrt = Q()
            f = ''
            statuses = request.query_params.getlist('Statuses', None)
            type = request.query_params.getlist('Types', None)
            severity = request.query_params.getlist('Severities', None)
            priority = request.query_params.getlist('Priorities', None)
            exclusive = request.query_params.get('Type of filter', None)
            sortby = request.query_params.getlist('SortBy', None)
            sortorder = request.query_params.get('SortOrder', None)
            filterissue = Q(creator=request.auth.user) | Q(asignedTo__username=request.auth.user) | Q(
                watchers__username=request.auth.user)

            if (exclusive == 'All Issues'):
                if sortby != None and sortorder != None and len(sortby) > 0 and (sortby[0] != '' or len(sortby) > 1):
                    for filtro in sortby:
                        if filtro != '' and filtro != None:
                            f = filtro.lower()
                            if (sortorder == 'desc'):
                                f = '-' + f
                if (f != ''):
                    issues = Issue.objects.filter(filterissue).order_by(f)
                else:
                    issues = Issue.objects.filter(filterissue)
                issues_serializer = self.serializer_class(issues, many=True)
                return Response(issues_serializer.data, status=status.HTTP_200_OK)

            else:
                if statuses != None and len(statuses) > 0 and (statuses[0] != '' or len(statuses) > 1):
                    for filtro in statuses:
                        if filtro != '':
                            f = traduce(filtro, "status")
                            if exclusive == 'Inclusive':
                                filtrosS = Q(status=f) | filtrosS
                            else:
                                filtrosS = Q(status=f) & filtrosS

                if priority != None and len(priority) > 0 and (priority[0] != '' or len(priority) > 1):
                    for filtro in priority:
                        if filtro != '':
                            f = traduce(filtro, "priority")
                            if exclusive == 'Inclusive':
                                filtrosP = Q(priority=f) | filtrosP
                            else:
                                filtrosP = Q(priority=f) & filtrosP

                if type != None and len(type) > 0 and (type[0] != '' or len(type) > 1):
                    for filtro in type:
                        if filtro != '':
                            f = traduce(filtro, "type")
                            if exclusive == 'Inclusive':
                                filtrosT = Q(type=f) | filtrosT
                            else:
                                filtrosT = Q(type=f) & filtrosT

                if severity != None and len(severity) > 0 and (severity[0] != '' or len(severity) > 1):
                    for filtro in severity:
                        if filtro != '' and filtro != None:
                            f = traduce(filtro, "severity")
                            if exclusive == 'Inclusive':
                                filtrosSv = Q(severity=f) | filtrosSv
                            else:
                                filtrosSv = Q(severity=f) & filtrosSv

                if sortby != None and sortorder != None and len(sortby) > 0 and (sortby[0] != '' or len(sortby) > 1):
                    if sortby[0] != '' and sortby[0] != None:
                        f = sortby[0].lower()
                        if (sortorder == 'desc'):
                            f = '-' + f

                creator = request.query_params.get('CreatedBy', None)

                if creator:
                    filtroscreator = creator.split(' ')
                    for filtro in filtroscreator:
                        if exclusive == 'Inclusive':
                            filtrosC = Q(creator=filtro) | filtrosC
                        else:
                            filtrosC = Q(creator=filtro) & filtrosC

                assigned = request.query_params.get('AssignedTo', None)

                if assigned:
                    filtrosasigned = assigned.split(' ')
                    for filtro in filtrosasigned:
                        user = User.objects.get(username=filtro)
                        if exclusive == 'Inclusive':
                            filtrosA = Q(asignedTo=user.id) | filtrosA
                        else:
                            filtrosA = Q(asignedTo=user.id) & filtrosA

                subject = request.query_params.get('Subject', None)

                if subject:
                    filtrosname = subject.split(' ')
                    for filtro in filtrosname:
                        if exclusive == 'Inclusive':
                            filtrosN = Q(subject=filtro) | filtrosN
                        else:
                            filtrosN = Q(subject=filtro) & filtrosN

                if exclusive == 'Inclusive':
                    filtrosF = (
                                           filtrosS | filtrosP | filtrosT | filtrosSv | filtrosC | filtrosA | filtrosN) & filterissue
                else:
                    filtrosF = (
                                           filtrosS & filtrosP & filtrosT & filtrosSv & filtrosC & filtrosA & filtrosN) & filterissue

                if sortby:
                    if subject:
                        issues = Issue.objects.order_by(f).filter(filtrosF).filter(Q(subject__icontains=subject))
                        issues_serializer = self.serializer_class(issues, many=True)
                        return Response(issues_serializer.data, status=status.HTTP_200_OK)
                    else:
                        issues = Issue.objects.order_by(f).filter(filtrosF)
                        issues_serializer = self.serializer_class(issues, many=True)
                        return Response(issues_serializer.data, status=status.HTTP_200_OK)
                else:
                    if subject:
                        issues = Issue.objects.filter(filtrosF).filter(Q(subject__icontains=subject))
                        issues_serializer = self.serializer_class(issues, many=True)
                        return Response(issues_serializer.data, status=status.HTTP_200_OK)
                    else:
                        issues = Issue.objects.filter(filtrosF)
                        issues_serializer = self.serializer_class(issues, many=True)
                        return Response(issues_serializer.data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            try:
                Issue.objects.get(id=id)
                return Response({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                return Response({'message': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        data = json.loads(request.body)
        if ('subject' in data):
            subject = data.get('subject')
            lines = subject.split(',')
            if (len(lines) > 1):
                for line in lines:
                    subject = line.strip()
                    if subject:
                        i = Issue(subject=subject, description=" ", creator=request.user.username, status=1, type=1,
                                  severity=1, priority=1)
                        i.save()
                return Response({'message': 'Issues created'}, status=status.HTTP_201_CREATED)
            else:
                subject = data.get('subject')

                if ('description' in data):
                    description = data.get('description')
                else:
                    return Response({'message': 'Description Missing'}, status=status.HTTP_400_BAD_REQUEST)
                if ('status' in data):
                    statuses = data.get('status')
                    if not check_in(statuses, "status"):
                        return Response({'message': 'Status not valid'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': 'Status Missing'}, status=status.HTTP_400_BAD_REQUEST)
                if ('type' in data):
                    type = data.get('type')
                    if not check_in(type, "type"):
                        return Response({'message': 'Type not valid'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': 'Type Missing'}, status=status.HTTP_400_BAD_REQUEST)

                if ('severity' in data):
                    severity = data.get('severity')
                    if not check_in(severity, "severity"):
                        return Response({'message': 'Severity not valid'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': 'Severity Missing'}, status=status.HTTP_400_BAD_REQUEST)

                if ('priority' in data):
                    priority = data.get('priority')
                    if not check_in(priority, "priority"):
                        return Response({'message': 'Priority not valid'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': 'Priority Missing'}, status=status.HTTP_400_BAD_REQUEST)

                statuses = traduce(statuses, "status")
                type = traduce(type, "type")
                severity = traduce(severity, "severity")
                priority = traduce(priority, "priority")

                i = Issue(subject=subject, description=description, creator=request.user.username, status=statuses,
                          type=type,
                          severity=severity, priority=priority)
                i.save()

                return Response({'message': 'Issue created'}, status=status.HTTP_201_CREATED)

        else:
            return Response({'message': 'Subject Missing'}, status=status.HTTP_400_BAD_REQUEST)

class AttachmentsAPIView(APIView):
    serializer_class = AttachmentsSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        try:
            issue = Issue.objects.get(id=id)
            tieneAcceso = check_user(id, request.auth.user)
            if tieneAcceso:
                documents = Attachments.objects.filter(issue=issue)
                documents_serializer = self.serializer_class(documents, many=True)
                return Response(documents_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': "You don't have permission to edit this Issue"},
                                status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response({'message': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, id):
        try:
            issue = Issue.objects.get(id=id)
            tieneAcceso = check_user(id, request.auth.user)
            if tieneAcceso:
                upfile = request.FILES.get('upfile')

                if (upfile != None):
                    # Obtener el archivo adjunto y otros campos del diccionario 'data'
                    file_name = upfile.name
                    file = Attachments.objects.filter(archivo=file_name, issue=issue).exists()
                    if not file:
                        document = Attachments(archivo=upfile, username=request.user.username, issue=issue)
                        document.save()
                    return Response({'message': 'Attachment added complete'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'message': 'Attachment empty, nothing was done'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': "You don't have permission to edit this Issue"},
                                status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response({'message': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)
    def delete(self, request, id):
        upfile = request.query_params.get('fileName', None)
        try:
            tieneAcceso = check_user(id, request.auth.user)
            if tieneAcceso:
                s3 = boto3.client('s3',
                                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
                object_name = upfile
                i = Issue.objects.get(id=id)
                tieneAcceso = check_user(id, request.auth.user)
                if tieneAcceso:
                    allAt = Attachments.objects.all().filter(archivo=object_name)
                    a = Attachments.objects.all().get(issue=i, archivo=object_name)
                    if (len(allAt) > 1):
                        a.delete()
                    elif (len(allAt) == 1):
                        a.delete()
                        s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=object_name)
                    return Response({'message': 'Attachment delete complete'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': "You don't have permission to edit this Issue"},
                                    status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'message': "You don't have permission to edit this Issue"},
                                status=status.HTTP_403_FORBIDDEN)
        except ClientError as e:
            return Response({'message': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            try:
                Issue.objects.get(id=id)
                return Response({'message': 'Attachment not found'}, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                return Response({'message': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)

class ActivityAPIView(APIView):
    serializer_class = ActivitySerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            issue_id = request.query_params.get('id', None)
            issue = Issue.objects.get(id=issue_id)
            user = User.objects.get(username=request.auth.user)
            is_assigned = issue.asignedTo.filter(id=user.id).exists()
            is_watcher = issue.watchers.filter(id=user.id).exists()
            if issue.getCreator() == user.username or is_assigned or is_watcher:
                activities = Activity.objects.filter(issueChanged=issue)
                activity_serializer = self.serializer_class(activities, many=True)
                return Response(activity_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You don\'t have permissions to view this issue'},
                                status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response({'message': 'No issues found'}, status=status.HTTP_404_NOT_FOUND)

class CommentsAPIView(APIView):
    serializer_class = CommentsSerializer
    permission_classes = (IsAuthenticated,)
    def post(self, request, id):
        try:
            issueId = Issue.objects.get(id=id)
            data = json.loads(request.body)
            if ('comment' in data):
                comment = data.get('comment')
                if len(comment) > 0:
                    user = User.objects.get(username=request.auth.user)
                    c = Comentario(message=comment, creator=user, issue=issueId)
                    c.save()
                    return Response({'message': 'New comment'}, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            return Response({'message': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, id):
        try:
            issueId = Issue.objects.get(id=id)
            comment = Comentario.objects.all().order_by('-creationDate').filter(issue=id)
            comment_serializer = self.serializer_class(comment, many=True)
            return Response(comment_serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'message': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)


class ProfileAPIView(APIView):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, usernameProf):
        try:
            user = User.objects.get(username=usernameProf)
            profile = Profile.objects.get(user=user)
            profile_serializer = self.serializer_class(profile)

            activities = Activity.objects.filter(user=user).order_by('-creationdate')
            activity_serializer = ActivitySerializer(activities, many=True)

            watchers = Issue.objects.filter(watchers=user)
            watcher_serializer = IssueSerializer(watchers, many=True)

            response_data = {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name
                },
                'profile': profile_serializer.data,
                'profile_image': {
                    'url_image': profile.get_url_image()
                },
                'profile_activity': {
                    'timeline': activity_serializer.data,
                    'watchers': watcher_serializer.data
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'message': 'No profile found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, usernameProf):
        try:
            user = User.objects.get(username=usernameProf)
            data = request.data

            if user == request.user:
                profile = Profile.objects.get(user=user)
                if 'profile' in request.FILES:
                    image = request.FILES['profile']
                    if image.content_type in ["image/jpeg", "image/png", "image/gif"]:
                        profile.image = image
                        profile.saveProfImg()
                        return Response({'message': 'Profile update complete'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'message': 'Unsupported media type'},
                                        status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
                else:
                    if 'bio' in data:
                        profile.bio = data.get('bio')
                        profile.save()
                    if 'email' in data:
                        user.email = data.get('email')
                        user.save()
                    if 'first_name' in data:
                        user.first_name = data.get('first_name')
                        user.save()
                    return Response({'message': 'Profile update complete'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You don\'t have permissions to edit this profile'},
                                status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response({'message': 'No profile found'}, status=status.HTTP_404_NOT_FOUND)

def check_user(id, user):
    issue = Issue.objects.get(id=id)  # Pillo la issue
    is_assigned = False
    is_watcher = False
    user = User.objects.get(username=user)  # pillo el user
    if (issue.getAsignedTo().name != None):  # compruebo si el user esta dentro de asigned
        is_assigned = issue.assignedTo.filter(id=user.id).exists()
    if (issue.getWatchers().name != None):  # compruebo si el user esta dentro de watchers
        is_watcher = issue.watchers.filter(id=user.id).exists()
    if issue.getCreator() == user.username or is_assigned or is_watcher:
        return True
    else:
        return False

def traduce(param, type):
    STATUSES = (
        ('New', 1), ('In progress', 2),
        ('Ready for test', 3), ('Closed', 4),
        ('Needs info', 5), ('Rejected', 6), ('Postponed', 7),
    )
    TYPES = (
        ('Bug', 1), ('Question', 2), ('Disabled', 3),
    )
    SEVERITIES = (
        ('Whishlist', 1), ('Minor', 2), ('Normal', 3),
        ('Important', 4), ('Critical', 5),
    )
    PRIORITIES = (
        ('Low', 1), ('Normal', 2), ('High', 3),
    )

    if (type == "status"):
        num = dict(STATUSES).get(param)
        return num
    elif (type == "type"):
        num = dict(TYPES).get(param)
        return num
    elif (type == "severity"):
        num = dict(SEVERITIES).get(param)
        return num
    elif (type == "priority"):
        num = dict(PRIORITIES).get(param)
        return num

def check_in(param, type):
    STATUSES = (
        ('New', 1), ('In progress', 2),
        ('Ready for test', 3), ('Closed', 4),
        ('Needs info', 5), ('Rejected', 6), ('Postponed', 7),
    )
    TYPES = (
        ('Bug', 1), ('Question', 2), ('Disabled', 3),
    )
    SEVERITIES = (
        ('Whishlist', 1), ('Minor', 2), ('Normal', 3),
        ('Important', 4), ('Critical', 5),
    )
    PRIORITIES = (
        ('Low', 1), ('Normal', 2), ('High', 3),
    )

    if type == "status":
        if param in [status[0] for status in STATUSES]:
            return True
        else:
            return False
    elif type == "type":
        if param in [types[0] for types in TYPES]:
            return True
        else:
            return False
    elif type == "severity":
        if param in [severity[0] for severity in SEVERITIES]:
            return True
        else:
            return False
    elif type == "priority":
        if param in [priority[0] for priority in PRIORITIES]:
            return True
        else:
            return False
    return False
