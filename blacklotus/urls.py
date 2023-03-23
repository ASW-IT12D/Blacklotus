from django.urls import path
from . import views

#URLConf
urlpatterns = [
    path('newissue/', views.CreateIssue),
    path('', views.CreateIssue)
]