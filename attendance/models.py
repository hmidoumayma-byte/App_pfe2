from django.db import models
from django.utils import timezone
from accounts.models import User, StudentProfile, TeacherProfile
import uuid
import qrcode
import io
from django.core.files.base import ContentFile


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Département'


class Module(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='modules')
    department = models.CharField(max_length=100, default='Génie Informatique')
    year_of_study = models.IntegerField(default=1)
    group = models.CharField(max_length=10, blank=True)
    total_hours = models.IntegerField(default=30)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_enrolled_students(self):
        return StudentProfile.objects.filter(
            year_of_study=self.year_of_study,
            department=self.department
        )

    class Meta:
        verbose_name = 'Module'


class Session(models.Model):
    SESSION_TYPES = [
        ('cours', 'Cours'),
        ('td', 'TD'),
        ('tp', 'TP'),
        ('examen', 'Examen'),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='sessions')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    session_type = models.CharField(max_length=10, choices=SESSION_TYPES, default='cours')
    room = models.CharField(max_length=50, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True)
    qr_expires_at = models.DateTimeField(null=True, blank=True)
    is_qr_active = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.module.code} - {self.date} {self.start_time}"

    def generate_qr_code(self, expiry_minutes=30):
        from django.conf import settings
        self.qr_expires_at = timezone.now() + timezone.timedelta(minutes=expiry_minutes)
        self.is_qr_active = True

        qr_data = f"http://192.168.1.111:8000/attendance/scan/{self.qr_token}/"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        filename = f'qr_{self.qr_token}.png'
        self.qr_code.save(filename, ContentFile(buffer.read()), save=False)
        self.save()
        return self

    def deactivate_qr(self):
        self.is_qr_active = False
        self.save()

    def is_qr_valid(self):
        if not self.is_qr_active:
            return False
        if self.qr_expires_at and timezone.now() > self.qr_expires_at:
            self.deactivate_qr()
            return False
        return True

    class Meta:
        verbose_name = 'Séance'
        ordering = ['-date', '-start_time']


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Présent'),
        ('absent', 'Absent'),
        ('late', 'En retard'),
        ('justified', 'Absences justifiée'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendances')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    scan_time = models.DateTimeField(null=True, blank=True)
    scan_ip = models.GenericIPAddressField(null=True, blank=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.session} - {self.get_status_display()}"

    class Meta:
        unique_together = ['student', 'session']
        verbose_name = 'Présence'
        ordering = ['-created_at']


class Justification(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvée'),
        ('rejected', 'Rejetée'),
    ]

    REASON_CHOICES = [
        ('medical', 'Raison médicale'),
        ('family', 'Raison familiale'),
        ('transport', 'Problème de transport'),
        ('administrative', 'Raison administrative'),
        ('other', 'Autre'),
    ]

    attendance = models.OneToOneField(Attendance, on_delete=models.CASCADE, related_name='justification')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default='other')
    description = models.TextField()
    document = models.FileField(upload_to='justifications/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_comment = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_justifications')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Justif - {self.student} - {self.attendance.session}"

    class Meta:
        verbose_name = 'Justification'
        ordering = ['-submitted_at']
