from django.urls import path
from . import views

app_name = 'core'  # Namespace to avoid URL name conflicts across apps

urlpatterns = [
    # Homepage — the entry point of the application
    path('', views.home, name='home'),

    # Custom registration view (login/logout are handled by django.contrib.auth.urls)
    path('register/', views.register, name='register'),
]
