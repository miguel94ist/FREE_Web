from free.views.base import LoginView, LogoutView
from django.urls import path

from . import views

app_name = 'free'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('api/v1/experiments', views.ExperimentListAPI.as_view(), name='api-experiment-list'),
]