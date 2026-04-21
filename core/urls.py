from django.urls import path
from . import views

app_name = 'core'  # Namespace to avoid URL name conflicts across apps

urlpatterns = [
    # Homepage — the entry point of the application
    path('', views.home, name='home'),
]
