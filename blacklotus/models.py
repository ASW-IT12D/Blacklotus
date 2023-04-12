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
    subject = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    creator = models.CharField(max_length=100)
    status = models.IntegerField()
    type = models.IntegerField()
    severity = models.IntegerField()
    priority = models.IntegerField()
    creationdate = models.DateTimeField(auto_now_add=True)
    modifieddate = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    asignedTo = models.ManyToManyField(User,blank=True)
    blocked = models.BooleanField(default= False)
    blockmotive = models.CharField(null=True, max_length=100, blank=True,default=False)
    deadline = models.BooleanField(default= False)
    deadlinedate = models.DateTimeField(null=True)

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

    def getAsignedTo(self):
        return self.asignedTo

    def getStatus(self):
        return self.status

    def getType(self):
        return self.type

    def getId(self):
        return self.id

    def getSeverity(self):
        return self.severity

    def getPriority(self):
        return self.priority

    def getEditionDate(self):
        return self.creationdate

    def __str__(self):
        return self.subject + ' ' + self.description


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Activity(models.Model):
    creationdate = models.DateTimeField(auto_now_add=True)
    field = models.CharField(max_length=100)
    change = models.CharField(max_length=100)
    old = models.CharField(max_length=100)
    user = models.CharField(max_length=100)
    issueChanged = models.ForeignKey(Issue, on_delete=models.CASCADE)
    objects = models.Manager()

    def getUser(self):
        return self.user

    def getField(self):
        return self.field

    def getChange(self):
        return self.change

    def getOld(self):
        return self.old

    def getDate(self):
        return self.creationdate


class Attachments(models.Model):
    archivo = models.FileField(upload_to='Attachments/')
    creado_en = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=100)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          aws_session_token=settings.AWS_SESSION_TOKEN)
        nombre_archivo = f"Attachments/{self.archivo.name}"
        with self.archivo.open('rb') as archivo:
            contenido = archivo.read()
        s3.put_object(Body=contenido, Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=nombre_archivo)
        self.archivo = nombre_archivo
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

    def save(self, *args, **kwargs):
        if bool(self.image):
            s3 = boto3.client('s3',
                              aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                              aws_session_token=settings.AWS_SESSION_TOKEN)
            nombre_archivo = f"Images/{self.image.name}"
            with self.image.open('rb') as archivo:
                contenido = archivo.read()
            s3.put_object(Body=contenido, Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=nombre_archivo)

            self.image = nombre_archivo

        super().save(*args, **kwargs)

    def get_url_image(self):
        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          aws_session_token=settings.AWS_SESSION_TOKEN)
        if bool(self.image):
            filename = self.image.name
        else:
            filename = 'Images/default.png'
        url = ''
        try:
            url = s3.generate_presigned_url('get_object',
                                            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                    'Key': filename},
                                            ExpiresIn=3600)  # la URL expirará en 1 hora
            return url
        except ClientError as e:
            print(e)