from django.db import models

# Create your models here.

class Issue(models.Model):
    subject = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    creator = models.CharField(max_length=100)

    objects = models.Manager()

    def getSubject(self):
        return self.subject
    def __str__(self):
        return self.subject + ' ' + self.description

class User(models.Model):
    username = models.CharField(max_length=100, primary_key=True)
    password = models.CharField(max_length=100)

    objects = models.Manager()

    def __str__(self):
        return self.username