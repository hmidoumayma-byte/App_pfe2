# academic/models.py
from django.db import models
from accounts.models import TeacherProfile

class Filiere(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.code} — {self.name}'
    class Meta: verbose_name = 'Filière'; ordering = ['code']

class Niveau(models.Model):
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='niveaux')
    name = models.CharField(max_length=50)  # ex: '1ère Année'
    year_number = models.IntegerField()      # 1, 2, 3, 4, 5
    max_absence_percent = models.FloatField(default=30.0)
    def __str__(self): return f'{self.filiere.code} — {self.name}'
    class Meta: verbose_name = 'Niveau'; unique_together = ['filiere', 'year_number']

class Groupe(models.Model):
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE, related_name='groupes')
    name = models.CharField(max_length=20)   # ex: 'G1'
    max_students = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    def __str__(self): return f'{self.niveau.filiere.code}/{self.niveau.year_number}/{self.name}'
    class Meta: verbose_name = 'Groupe'; unique_together = ['niveau', 'name']

class Salle(models.Model):
    TYPES = [('amphi','Amphithéâtre'),('salle','Salle de cours'),
             ('labo','Laboratoire'),('tp','Salle TP')]
    name = models.CharField(max_length=50, unique=True)
    capacity = models.IntegerField(default=30)
    room_type = models.CharField(max_length=10, choices=TYPES, default='salle')
    building = models.CharField(max_length=50, blank=True)
    floor = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return f'{self.name} ({self.get_room_type_display()}, {self.capacity} places)'

class EmploiDuTemps(models.Model):
    JOURS = [('lun','Lundi'),('mar','Mardi'),('mer','Mercredi'),
             ('jeu','Jeudi'),('ven','Vendredi'),('sam','Samedi')]
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, related_name='emploi_du_temps')
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='emploi_du_temps')
    module_name = models.CharField(max_length=200)
    salle = models.ForeignKey(Salle, on_delete=models.SET_NULL, null=True, blank=True)
    jour = models.CharField(max_length=3, choices=JOURS)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    session_type = models.CharField(max_length=10,
        choices=[('cours','Cours'),('td','TD'),('tp','TP')], default='cours')
    semester = models.IntegerField(default=1, choices=[(1,'S1'),(2,'S2')])
    is_active = models.BooleanField(default=True)
    class Meta: verbose_name = 'Emploi du temps'; ordering = ['jour','heure_debut']
