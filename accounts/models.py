from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    """Modèle utilisateur personnalisé avec rôles"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('teacher', 'Enseignant'),
        ('student', 'Étudiant'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    def is_admin(self):
        return self.role == 'admin'

    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'

    def save(self, *args, **kwargs):
        # Générer automatiquement le username si non fourni
        if not self.username and self.email:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)


class StudentProfile(models.Model):
    """Profil étudiant avec lien vers le groupe académique"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='student_profile'
    )
    
    # Anciens champs conservés pour compatibilité
    student_id = models.CharField(max_length=20, unique=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    year_of_study = models.IntegerField(default=1)
    group = models.CharField(max_length=20, blank=True)  # Ancien champ
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    phone_secondary = models.CharField(max_length=20, blank=True)  # Contact parent
    emergency_contact = models.CharField(max_length=100, blank=True)
    institutional_code = models.CharField(max_length=30, blank=True)
    identity_photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=True)

    # =====================================================
    # NOUVEAU — Lien vers le vrai groupe académique
    # =====================================================
    groupe_academique = models.ForeignKey(
        'academic.Groupe',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='etudiants',
        verbose_name='Groupe Académique'
    )

    class Meta:
        verbose_name = 'Profil Étudiant'
        verbose_name_plural = 'Profils Étudiants'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.student_id or 'Sans ID'}"

    def get_absence_percentage(self, module=None):
        """Calcule le pourcentage d'absences"""
        from attendance.models import Attendance, Session
        
        if module:
            total_sessions = Session.objects.filter(module=module).count()
            absences = Attendance.objects.filter(
                student=self, 
                session__module=module, 
                status='absent'
            ).count()
        else:
            total_sessions = Session.objects.count()
            absences = Attendance.objects.filter(
                student=self, 
                status='absent'
            ).count()

        if total_sessions == 0:
            return 0
        return round((absences / total_sessions) * 100, 2)

    @property
    def full_name(self):
        """Retourne le nom complet de l'étudiant"""
        return self.user.get_full_name()

    @property
    def email(self):
        """Retourne l'email de l'étudiant"""
        return self.user.email


class TeacherProfile(models.Model):
    """Profil enseignant"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='teacher_profile'
    )
    
    teacher_id = models.CharField(max_length=20, unique=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = 'Profil Enseignant'
        verbose_name_plural = 'Profils Enseignants'

    def __str__(self):
        return f"Prof. {self.user.get_full_name()}"

    @property
    def full_name(self):
        """Retourne le nom complet de l'enseignant"""
        return self.user.get_full_name()


class PasswordResetToken(models.Model):
    """Token de réinitialisation de mot de passe"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='password_reset_tokens'
    )
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Token de Réinitialisation'
        verbose_name_plural = 'Tokens de Réinitialisation'

    def __str__(self):
        return f"Token pour {self.user.email}"

    def is_valid(self):
        """Vérifie si le token est encore valide (24h)"""
        return (
            not self.is_used and 
            (timezone.now() - self.created_at) < timedelta(hours=24)
        )

    def mark_as_used(self):
        """Marque le token comme utilisé"""
        self.is_used = True
        self.save(update_fields=['is_used'])