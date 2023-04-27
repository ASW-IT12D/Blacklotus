from django.urls import path
from . import views
from .views import ProfileEditView
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from .views import IssueAPIView
#URLConf
urlpatterns = [
    path('register/', views.join, name='register'),
    path('',views.log, name = 'login'),
    path('login/',views.redirectLogin, name = 'login'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('logout/',views.custom_logout, name='logout'),
    path('<str:usernameProf>',views.showProfile, name = 'profile'),
    path('accounts/profile/',views.showProfileRedir, name = 'profileR'),
    path('Edit/',ProfileEditView.as_view(), name='editprofile'),
    path('Issues/', views.showIssues,name='home'),
    path('NewIssue/', views.CreateIssueForm, name="newIssue"),
    path('BulkIssues/', views.BulkIssueForm, name="bulkIssue"),
    path('Issue/<int:num>/', views.SeeIssue, name="seeIssue"),
    path('Issue/<int:id>/BlockIssue/', views.BlockIssueForm, name="blockIssue"),
    path('Issue/<int:id>/Edit/', views.EditIssue, name='edit'),
    path('Issue/<int:id>/Deadline/', views.deadLineForm, name = 'deadline'),
    path('api/Issue/',IssueAPIView.as_view())
]