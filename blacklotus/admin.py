from django.contrib import admin
from .models import Issue
from .models import CustomUser
admin.site.register(Issue)
admin.site.register(CustomUser)
# Register your models here.
