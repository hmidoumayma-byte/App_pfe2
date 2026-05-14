# academic/urls.py
from django.urls import path
from . import views
app_name = 'academic'

urlpatterns = [
    path('filieres/', views.filiere_list, name='filiere_list'),
    path('filieres/create/', views.filiere_create, name='filiere_create'),
    path('filieres/<int:pk>/edit/', views.filiere_edit, name='filiere_edit'),
    path('niveaux/', views.niveau_list, name='niveau_list'),
    path('niveaux/create/', views.niveau_create, name='niveau_create'),
    path('groupes/', views.groupe_list, name='groupe_list'),
    path('groupes/create/', views.groupe_create, name='groupe_create'),
    path('salles/', views.salle_list, name='salle_list'),
    path('salles/create/', views.salle_create, name='salle_create'),
    path('emploi-du-temps/', views.emploi_du_temps, name='emploi_du_temps'),
    path('emploi-du-temps/create/', views.emploi_create, name='emploi_create'),
]
