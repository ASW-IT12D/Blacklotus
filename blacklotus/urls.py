from django.urls import path
from . import views

#URLConf
urlpatterns = [
    path('newissue/', views.CreateIssueForm, name="newIssue"),
    path('showIssues/', views.showIssues,name='home'),
    path('delete/<int:id>', views.DeleteIssue, name="deleteIssue"),
    path('newissue/new/', views.CreateIssue),
    path('<int:num>/', views.SeeIssue, name="seeIssue"),
    path('register/', views.join, name='register'),
    path('',views.log, name = 'login')
]