from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('api/v1/experiments', views.ExperimentListAPI.as_view(), name='api-experiment-list'),
]