import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'absence_app.settings')
django.setup()

from attendance.models import Attendance, Session
from notifications.models import Notification

absences = Attendance.objects.filter(status='absent').select_related('student__user', 'session__module')

count = 0
for att in absences:
    student = att.student
    session = att.session
    module = session.module

    total_sessions = Session.objects.filter(module=module).count()
    total_absences = Attendance.objects.filter(student=student, session__module=module, status='absent').count()
    taux = round((total_absences / total_sessions * 100), 1) if total_sessions > 0 else 0

    Notification.objects.get_or_create(
        user=student.user,
        title=f'Absence — {module.code}',
        message=f'Absent le {session.date} — {module.name}.',
        notification_type='absence',
    )
    count += 1

    if taux >= 50:
        Notification.objects.get_or_create(
            user=student.user,
            title=f'CRITIQUE — {module.code}',
            message=f'Taux d absence {taux}% dans {module.name}. Contactez administration !',
            notification_type='alert',
        )
    elif taux >= 30:
        Notification.objects.get_or_create(
            user=student.user,
            title=f'Alerte — {module.code}',
            message=f'Taux d absence {taux}% dans {module.name}. Seuil dangereux !',
            notification_type='alert',
        )

print(f'✅ {count} notifications créées !')