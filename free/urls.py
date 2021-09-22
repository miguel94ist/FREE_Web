from free.views.base import LoginView, LogoutView
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from . import views

# Helper function to generate API documentation
schema_view = get_schema_view(
   openapi.Info(
      title="FREE API",
      default_version='v1',
      description="Documentation for FREE API endpoints",
      terms_of_service="https://#/",
      contact=openapi.Contact(email="pavel.kuriscak@gmail.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

app_name = 'free'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),

    # API DOCUMENTATION
    re_path(r'^free-api(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^api/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^api/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # REST API
    path('api/v1/experiments', views.ExperimentListAPI.as_view(), name='api-experiment-list'),
    path('api/v1/execution', views.ExecutionConfigure.as_view(), name='api-execution-configure' ),
    path('api/v1/execution/<int:id>', views.ExecutionStart.as_view(), name='api-execution-start'),
    path('api/v1/execution/<int:id>/status', views.ExecutionStatus.as_view(), name='api-execution-status'),
]