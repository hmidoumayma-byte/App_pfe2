# messaging/models.py
from django.db import models
from accounts.models import User

class Conversation(models.Model):
    TYPES = [('student_teacher','Étudiant->Enseignant'),
             ('student_admin','Étudiant->Administration'),
             ('teacher_student','Enseignant->Étudiant')]
    participants = models.ManyToManyField(User, related_name='conversations')
    subject = models.CharField(max_length=200)
    conv_type = models.CharField(max_length=20, choices=TYPES, default='student_teacher')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    def get_last_message(self): return self.messages.order_by('-sent_at').first()
    class Meta: ordering = ['-updated_at']; verbose_name = 'Conversation'

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    class Meta: ordering = ['sent_at']; verbose_name = 'Message'
