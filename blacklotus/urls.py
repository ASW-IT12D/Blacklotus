from django.urls import path
from . import views
from .views import ProfileEditView, AttachmentsAPIView
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from .views import IssueAPIView, ActivityAPIView,ProfileAPIView,IssuesAPIView,CommentsAPIView
from rest_framework.authtoken.views import obtain_auth_token
#URLConf
urlpatterns = [
    path('register/', views.join, name='register'),
    path('',views.log, name = 'login'),
    path('login/',views.redirectLogin, name = 'login'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('logout/',views.custom_logout, name='logout'),
    path('<str:usernameProf>',views.showProfile, name = 'profile'),
    path('accounts/profile/',views.showProfileRedir, name = 'profileR'),
    path('edit/',ProfileEditView.as_view(), name='editprofile'),
    path('issues1/', views.showIssues,name='home'),
    path('newIssue/', views.CreateIssueForm, name="newIssue"),
    path('bulk_issues/', views.BulkIssueForm, name="bulkIssue"),
    path('issue1/<int:num>/', views.SeeIssue, name="seeIssue"),
    path('issue/<int:id>/BlockIssue/', views.BlockIssueForm, name="blockIssue"),
    path('issue/<int:id>/Edit/', views.EditIssue, name='edit'),
    path('issue/<int:id>/Deadline/', views.deadLineForm, name = 'deadline'),
    path('issue/<int:id>/', include(
        [
            path('', IssueAPIView.as_view(), name='api-issue'),
            path('attachment', AttachmentsAPIView.as_view(), name='api-Docu'),
        ]
    )),
    path('issues/', IssuesAPIView.as_view(), name='api-issue'),
    path('activity/',ActivityAPIView.as_view(),name='api-activity'),
    path('profile/<str:usernameProf>/',ProfileAPIView.as_view(),name='api-profile'),
    path('api/token/',obtain_auth_token,name='api-token'),
    path('token/', views.get_token,name='token'),
    path('comment/<int:id>/', CommentsAPIView.as_view(), name='api-comments')
]