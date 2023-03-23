from django.urls import path
from . import views

#URLConf
urlpatterns = [
    path('newissue/', views.CreateIssueForm),
    path('', views.showIssues),
    path('newissue/newissue/new/', views.CreateIssue)
]