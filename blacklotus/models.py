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

class Comentario(models.Model):
    message = models.CharField(max_length=100)
    creator = models.CharField(max_length=100)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    creationDate = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def getCreator(self):
        return self.creator

    def getMessage(self):
        return self.message

    def getCreationDate(self):
        return self.creationDate