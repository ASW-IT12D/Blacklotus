from django.urls import path
from . import views
from .views import ProfileEditView
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
#URLConf
urlpatterns = [
    path('newissue/', views.CreateIssueForm, name="newIssue"),
    path('bulkissue/', views.BulkIssueForm, name="bulkIssue"),
    path('<int:id>/blockissue/', views.BlockIssueForm, name="blockIssue"),
    path('showIssues/', views.showIssues,name='home'),
    path('delete/<int:id>', views.DeleteIssue, name="deleteIssue"),
    path('newissue/new/', views.CreateIssue),
    path('bulkissue/new/', views.BulkIssue),
    path('<int:num>/', views.SeeIssue, name="seeIssue"),
    path('register/', views.join, name='register'),
    path('',views.log, name = 'login'),
    path('login/',views.redirectLogin, name = 'login'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('logout/',views.custom_logout, name='logout'),
    path('accounts/<str:username>',views.showProfile, name = 'profile'),
    path('editprofile/',ProfileEditView.as_view(), name='editprofile'),
    path('edit/', views.EditIssue, name='edit'),
    path('<int:id>/deadline/', views.deadLineForm, name = 'deadline')
]