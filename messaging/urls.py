# messaging/urls.py
from django.urls import path
from . import views
app_name = 'messaging'
urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('conversation/<int:pk>/', views.conversation_detail, name='conversation'),
    path('new/', views.new_conversation, name='new'),
]
