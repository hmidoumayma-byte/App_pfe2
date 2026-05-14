# core_settings/urls.py
from django.urls import path
from . import views
app_name = 'core_settings'

urlpatterns = [
    path('settings/', views.system_settings, name='settings'),
    path('logs/', views.action_logs, name='logs'),
    path('backup/', views.backup_data, name='backup'),
]
