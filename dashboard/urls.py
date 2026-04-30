from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('ai-analysis/', views.ai_analysis, name='ai_analysis'),
]