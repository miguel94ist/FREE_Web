from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


class LoginView(auth_views.LoginView):
    template_name = 'free/login.html'

class LogoutView(auth_views.LogoutView):
    pass