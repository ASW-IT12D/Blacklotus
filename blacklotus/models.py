import os
import os

from botocore.exceptions import ClientError
from django.core.files.base import ContentFile
from django.conf import settings
import boto3
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.

class Issue(models.Model):
    STATUSES = (
        (1, 'New'), (2,'In progress'),
        (3,'Ready for test'), (4,'Closed'),
        (5,'Needs info'), (6,'Rejected'), (7,'Postponed'),
    )
    TYPES = (
        (1,'Bug'), (2,'Question'), (3,'Disabled'),
    )
    SEVERITIES = (
        (1,'Whishlist'),(2,'Minor'),(3,'Normal'),
        (4,'Important'),(5,'Critical'),
    )
    PRIORITIES = (
        (1,'Low'),(2,'Normal'),(3,'High'),
    )


    subject = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    creator = models.CharField(max_length=100)

    status = models.IntegerField(choices=STATUSES)
    type = models.IntegerField(choices=TYPES)
    severity = models.IntegerField(choices=SEVERITIES)
    priority = models.IntegerField(choices=PRIORITIES)

    creationdate = models.DateTimeField(auto_now_add=True)
    modifieddate = models.DateTimeField(auto_now=True)
    deadlinedate = models.DateTimeField(null=True, blank=True)
    deadlinemotive = models.CharField(max_length=100)
    objects = models.Manager()
    asignedTo = models.ManyToManyField(User,blank=True, related_name="assigned_issues")
    blocked = models.BooleanField(default= False)
    blockmotive = models.CharField(null=True, max_length=100, blank=True,default=False)
    deadline = models.BooleanField(default= False)
    watchers = models.ManyToManyField(User, blank=True, related_name ="watchers_issue")

    def getFirstAsign(self):
        return self.asignedTo.first()

    def getSubject(self):
        return self.subject

    def getBlocked(self):
        return self.blocked

    def getDeadline(self):
        return self.deadline

    def getDateDeadLine(self):
        return self.deadlinedate

    def getDescription(self):
        return self.description

    def getCreator(self):
        return self.creator

    def getWatchers(self):
        return self.watchers

    def getAsignedTo(self):
        return self.asignedTo


    def getStatus(self):
        status_num = self.status
        status_text = dict(self.STATUSES).get(status_num)
        return status_text

    def getType(self):
        type_num = self.type
        type_text = dict(self.TYPES).get(type_num)
        return type_text

    def getId(self):
        return self.id

    def getSeverity(self):
        severity_num = self.severity
        severity_text = dict(self.SEVERITIES).get(severity_num)
        return severity_text

    def getPriority(self):
        priority_num = self.priority
        priority_text = dict(self.PRIORITIES).get(priority_num)
        return priority_text

    def getEditionDate(self):
        return self.creationdate

    def __str__(self):
        return self.subject + ' ' + self.description


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Activity(models.Model):
    STATUSES = (
        (1, 'New'), (2,'In progress'),
        (3,'Ready for test'), (4,'Closed'),
        (5,'Needs info'), (6,'Rejected'), (7,'Postponed'),
    )
    TYPES = (
        (1,'Bug'), (2,'Question'), (3,'Disabled'),
    )
    SEVERITIES = (
        (1,'Whishlist'),(2,'Minor'),(3,'Normal'),
        (4,'Important'),(5,'Critical'),
    )
    PRIORITIES = (
        (1,'Low'),(2,'Normal'),(3,'High'),
    )

    creationdate = models.DateTimeField(auto_now_add=True)
    field = models.CharField(max_length=100)
    change = models.CharField(max_length=100)
    old = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issueChanged = models.ForeignKey(Issue, on_delete=models.CASCADE)
    objects = models.Manager()

    def getUser(self):
        return self.user

    def getField(self):
        return self.field

    def getChange(self):
        if (self.field == "status"):
            status_num = int(self.change)
            status_text = dict(self.STATUSES).get(status_num)
            return status_text
        elif (self.field == "severity"):
            severity_num = int(self.change)
            severity_text = dict(self.SEVERITIES).get(severity_num)
            return severity_text
        elif (self.field == "type"):
            type_num = int(self.change)
            type_text = dict(self.TYPES).get(type_num)
            return type_text
        elif (self.field == "priority"):
            priority_num = int(self.change)
            priority_text = dict(self.PRIORITIES).get(priority_num)
            return priority_text
        else:
            return self.change
    def getOld(self):
        return self.old

    def getDate(self):
        return self.creationdate

    def getIssueChangedSubject(self):
        return self.issueChanged.getSubject()

class Attachments(models.Model):
    archivo = models.FileField(upload_to='Attachments/')
    creado_en = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=100)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        nombre_archivo = f"Attachments/{self.archivo.name}"
        with self.archivo.open('rb') as archivo:
            contenido = archivo.read()
        s3.put_object(Body=contenido, Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=nombre_archivo)
        nombre = self.archivo.name
        self.archivo = nombre
        super().save(*args, **kwargs)

class Comentario(models.Model):
    message = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    creationDate = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


    def getCreator(self):
        return self.creator

    def getMessage(self):
        return self.message

    def getCreationDate(self):
        return self.creationDate

class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    bio = models.TextField()
    image = models.ImageField(upload_to='Images/', blank=True)
    objects = models.Manager()

    def __str__(self):
        return str(self.user)

    def saveProfImg(self, *args, **kwargs):
        if bool(self.image):
            s3 = boto3.client('s3',
                              aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            nombre_archivo = f"Images/{self.image.name}"
            with self.image.open('rb') as archivo:
                contenido = archivo.read()
            s3.put_object(Body=contenido, Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=nombre_archivo)
            self.image = nombre_archivo
        super().save(*args, **kwargs)

    def get_user(self):
        return self.user
    def get_bio(self):
        return self.bio
    def get_url_image(self):
        try:
            s3 = boto3.client('s3',
                              aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            if bool(self.image):
                filename = self.image.name
            else:
                filename = 'Images/default.png'
            url = ''

            url = s3.generate_presigned_url('get_object',
                                            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                    'Key': filename},
                                            ExpiresIn=3600)  # la URL expirará en 1 hora
            return url
        except ClientError as e:
            print(e)