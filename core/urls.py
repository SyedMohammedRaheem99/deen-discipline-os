from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),

    # Tasks
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/toggle/<int:task_id>/', views.task_toggle, name='task_toggle'),
    path('tasks/delete/<int:task_id>/', views.task_delete, name='task_delete'),
    path('tasks/quick-add/', views.task_quick_add, name='task_quick_add'),

    # Prayers
    path('prayers/', views.prayer_list, name='prayer_list'),
    path('prayers/toggle/<int:prayer_id>/', views.prayer_toggle, name='prayer_toggle'),
    path('prayers/on-time/<int:prayer_id>/', views.prayer_on_time_toggle, name='prayer_on_time_toggle'),

    # Health
    path('health/water/', views.health_water_update, name='health_water_update'),
    path('health/workout/', views.health_workout_toggle, name='health_workout_toggle'),

    # Journal
    path('journal/', views.journal_view, name='journal_view'),
    path('journal/save/', views.journal_save, name='journal_save'),
    path('journal/delete/', views.journal_delete, name='journal_delete'),

    # Flow
    path('flow/', views.flow_view, name='flow'),
    path('flow/generate/', views.flow_generate, name='flow_generate'),
    path('flow/toggle/<int:block_id>/', views.flow_block_toggle, name='flow_block_toggle'),
]
