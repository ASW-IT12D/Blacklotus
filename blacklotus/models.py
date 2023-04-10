import os

from django.core.files.storage import default_storage
from django.conf import settings
import boto3
from django.db import models

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

    def getSubject(self):
        return self.subject
    def getDescription(self):
        return self.description
    def getCreator(self):
        return self.creator

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

class Attachments(models.Model):
    archivo = models.FileField(upload_to='Attachments/')
    creado_en = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=100)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

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

    def download(self, obj_name):
        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          aws_session_token=settings.AWS_SESSION_TOKEN)
        object_name = 'Attachments/'+obj_name
        # Obtener el nombre del archivo a descargar
        # Obtener la ruta del archivo actual
        current_file_path = os.path.abspath(__file__)

        # Obtener la ruta del directorio padre
        parent_dir_path = os.path.dirname(current_file_path)

        # Obtener la ruta del directorio padre del directorio padre (es decir, la raíz del proyecto)
        project_dir_path = os.path.dirname(parent_dir_path)
        file_name = project_dir_path+obj_name
        # Descargar el archivo desde S3
        s3.download_file(settings.AWS_STORAGE_BUCKET_NAME, object_name, file_name)

