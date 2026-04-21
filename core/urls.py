from django.urls import path
from . import views

app_name = 'core'  # Namespace to avoid URL name conflicts across apps

urlpatterns = [
    # Homepage — the entry point of the application
    path('', views.home, name='home'),

    # Custom registration view (login/logout are handled by django.contrib.auth.urls)
    path('register/', views.register, name='register'),

    # Task management
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/toggle/<int:task_id>/', views.task_toggle, name='task_toggle'),

    # Prayer tracking
    path('prayers/', views.prayer_list, name='prayer_list'),
    path('prayers/toggle/<int:prayer_id>/', views.prayer_toggle, name='prayer_toggle'),
    path('prayers/on-time/<int:prayer_id>/', views.prayer_on_time_toggle, name='prayer_on_time_toggle'),
]
