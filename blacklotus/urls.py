from django.urls import path
from . import views
from .views import ProfileEditView
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from .views import IssueAPIView, ActivityAPIView
#URLConf
urlpatterns = [
    path('register/', views.join, name='register'),
    path('',views.log, name = 'login'),
    path('login/',views.redirectLogin, name = 'login'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('logout/',views.custom_logout, name='logout'),
    #path('<str:usernameProf>',views.showProfile, name = 'profile'),
    #path('accounts/profile/',views.showProfileRedir, name = 'profileR'),
    #path('edit/',ProfileEditView.as_view(), name='editprofile'),
    #path('issues/', views.showIssues,name='home'),
    #path('newIssue/', views.CreateIssueForm, name="newIssue"),
    #path('bulk_issues/', views.BulkIssueForm, name="bulkIssue"),
    #path('issue/<int:num>/', views.SeeIssue, name="seeIssue"),
    #path('issue/<int:id>/BlockIssue/', views.BlockIssueForm, name="blockIssue"),
    #path('issue/<int:id>/Edit/', views.EditIssue, name='edit'),
    #path('issue/<int:id>/Deadline/', views.deadLineForm, name = 'deadline'),
    path('issue/',IssueAPIView.as_view()),
    path('activity/',ActivityAPIView.as_view())
]