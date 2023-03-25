from django.urls import path
from . import views

#URLConf
urlpatterns = [
    path('', views.loginPage,name='login'),
    path('signup/', views.signUp, name='signup')
]