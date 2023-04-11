from django.contrib import admin
from .models import Issue, Attachments,Profile
admin.site.register(Profile)
admin.site.register(Issue)
admin.site.register(Attachments)
# Register your models here.
