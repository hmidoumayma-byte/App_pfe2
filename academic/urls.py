from django.urls import path
from . import views

app_name = 'academic'

urlpatterns = [
    # Filières
    path('filieres/', views.filiere_list, name='filiere_list'),
    path('filieres/create/', views.filiere_create, name='filiere_create'),
    path('filieres/<int:pk>/edit/', views.filiere_edit, name='filiere_edit'),

    # Niveaux
    path('niveaux/', views.niveau_list, name='niveau_list'),
    path('niveaux/create/', views.niveau_create, name='niveau_create'),
    path('niveaux/<int:pk>/edit/', views.niveau_edit, name='niveau_edit'),

    # Groupes
    path('groupes/', views.groupe_list, name='groupe_list'),
    path('groupes/create/', views.groupe_create, name='groupe_create'),
    path('groupes/<int:pk>/edit/', views.groupe_edit, name='groupe_edit'),

    # Salles
    path('salles/', views.salle_list, name='salle_list'),
    path('salles/create/', views.salle_create, name='salle_create'),
    path('salles/<int:pk>/edit/', views.salle_edit, name='salle_edit'),

    # Emploi du temps
    path('emploi-du-temps/', views.emploi_du_temps, name='emploi_du_temps'),
    path('emploi-du-temps/create/', views.emploi_create, name='emploi_create'),
    path('emploi-du-temps/<int:pk>/delete/', views.emploi_delete, name='emploi_delete'),

    # API JSON pour selects dynamiques (inscription étudiant)
    path('api/niveaux/<int:filiere_id>/', views.api_niveaux_by_filiere, name='api_niveaux'),
    path('api/groupes/<int:niveau_id>/', views.api_groupes_by_niveau, name='api_groupes'),
]