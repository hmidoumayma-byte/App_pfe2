# core_settings/models.py
from django.db import models
from accounts.models import User

class SystemSettings(models.Model):
    institution_name = models.CharField(max_length=200, default='Mon Etablissement')
    institution_logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    institution_address = models.TextField(blank=True)
    institution_phone = models.CharField(max_length=30, blank=True)
    institution_email = models.EmailField(blank=True)
    academic_year = models.CharField(max_length=20, default='2024-2025')
    alert_threshold = models.FloatField(default=30.0)
    critical_threshold = models.FloatField(default=50.0)
    justification_deadline_days = models.IntegerField(default=7)
    allow_student_register = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    class Meta: verbose_name = 'Parametres systeme'
    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

class ActionLog(models.Model):
    ACTIONS = [('create_user','Creation utilisateur'),('delete_user','Suppression utilisateur'),
               ('update_user','Modification utilisateur'),('validate_justif','Validation justification'),
               ('reject_justif','Rejet justification'),('import_excel','Import Excel'),
               ('update_settings','Modification parametres'),('add_absence','Ajout absence manuel'),
               ('other','Autre')]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=30, choices=ACTIONS)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']; verbose_name = 'Log d action'

class Rappel(models.Model):
    TYPES = [('absence','Absence'),('session','Seance'),('justification','Justification')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rappels')
    rappel_type = models.CharField(max_length=20, choices=TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    reminder_date = models.DateTimeField()
    is_sent = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ['reminder_date']; verbose_name = 'Rappel'
