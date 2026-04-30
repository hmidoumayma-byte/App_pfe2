from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
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

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    def is_admin(self):
        return self.role == 'admin'

    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    year_of_study = models.IntegerField(default=1)
    group = models.CharField(max_length=10, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.student_id}"

    def get_absence_percentage(self, module=None):
        from attendance.models import Attendance, Session
        if module:
            total_sessions = Session.objects.filter(module=module).count()
            absences = Attendance.objects.filter(
                student=self, session__module=module, status='absent'
            ).count()
        else:
            total_sessions = Session.objects.count()
            absences = Attendance.objects.filter(student=self, status='absent').count()

        if total_sessions == 0:
            return 0
        return round((absences / total_sessions) * 100, 2)


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    teacher_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    specialization = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Prof. {self.user.get_full_name()}"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        from django.utils import timezone
        from datetime import timedelta
        return not self.is_used and \
               (timezone.now() - self.created_at) < timedelta(hours=24)
