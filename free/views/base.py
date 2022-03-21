from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.conf import settings
from pydoc import locate

class LoginView(auth_views.LoginView):
    template_name = 'free/login.html'

        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        auth_backends = []
        auth_backend_names = getattr(settings, "AUTHENTICATION_BACKENDS", None)
        for b in auth_backend_names:
            print(b)
            my_class = locate(b)
            try:
                print(my_class.name)
                auth_backends.append([my_class.name, my_class.name.replace('-', " ").upper() ])
            except:
                pass
        print(auth_backends)
        context['back_ends'] = auth_backends
        return context

class LogoutView(auth_views.LogoutView):
    pass
