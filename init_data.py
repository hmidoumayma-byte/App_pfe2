"""
Script de création des données initiales.
Exécuter avec: python manage.py shell < database/init_data.py
OU: python manage.py loaddata database/fixtures.json
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'absence_app.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from accounts.models import User, StudentProfile, TeacherProfile
from attendance.models import Module, Session, Attendance
from django.utils import timezone
from datetime import date, time, timedelta
import random

print("🚀 Création des données de test...")

# ── ADMIN ──────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create(
        username='admin',
        email='admin@gestiabsence.ma',
        first_name='Admin',
        last_name='Système',
        role='admin',
        is_staff=True,
        is_superuser=True,
    )
    admin.set_password('admin123')
    admin.save()
    print("✅ Admin créé: admin / admin123")

# ── ENSEIGNANTS ────────────────────────────────────────
teachers_data = [
    ('prof1', 'Ahmed', 'Benali', 'prof1@univ.ma', 'ENS001', 'Génie Informatique', 'Algorithmique'),
    ('prof2', 'Fatima', 'Ezzahra', 'prof2@univ.ma', 'ENS002', 'Génie Informatique', 'Réseaux'),
    ('prof3', 'Karim', 'Mansouri', 'prof3@univ.ma', 'ENS003', 'Génie Informatique', 'Base de données'),
]

teachers = []
for uname, fname, lname, email, tid, dept, spec in teachers_data:
    if not User.objects.filter(username=uname).exists():
        u = User.objects.create(
            username=uname, email=email,
            first_name=fname, last_name=lname,
            role='teacher'
        )
        u.set_password('prof123')
        u.save()
        tp = TeacherProfile.objects.create(
            user=u, teacher_id=tid, department=dept, specialization=spec
        )
        teachers.append(tp)
        print(f"✅ Enseignant: {uname} / prof123")
    else:
        teachers.append(User.objects.get(username=uname).teacher_profile)

# ── ÉTUDIANTS ──────────────────────────────────────────
students_data = [
    ('etud1', 'Mohammed', 'Alaoui',   'etud1@univ.ma', 'ETU001', 'Génie Informatique', 2, 'G1'),
    ('etud2', 'Sara',     'Tahiri',   'etud2@univ.ma', 'ETU002', 'Génie Informatique', 2, 'G1'),
    ('etud3', 'Yassine',  'Chraibi',  'etud3@univ.ma', 'ETU003', 'Génie Informatique', 2, 'G1'),
    ('etud4', 'Nadia',    'Bensouda', 'etud4@univ.ma', 'ETU004', 'Génie Informatique', 2, 'G2'),
    ('etud5', 'Omar',     'Filali',   'etud5@univ.ma', 'ETU005', 'Génie Informatique', 2, 'G2'),
    ('etud6', 'Amina',    'Lahlou',   'etud6@univ.ma', 'ETU006', 'Génie Informatique', 2, 'G1'),
]

students = []
for uname, fname, lname, email, sid, dept, yr, grp in students_data:
    if not User.objects.filter(username=uname).exists():
        u = User.objects.create(
            username=uname, email=email,
            first_name=fname, last_name=lname,
            role='student'
        )
        u.set_password('etud123')
        u.save()
        sp = StudentProfile.objects.create(
            user=u, student_id=sid, department=dept,
            year_of_study=yr, group=grp
        )
        students.append(sp)
        print(f"✅ Étudiant: {uname} / etud123")
    else:
        students.append(User.objects.get(username=uname).student_profile)

# ── MODULES ────────────────────────────────────────────
if teachers:
    modules_data = [
        ('INFO201', 'Algorithmique Avancée',    teachers[0], 'Génie Informatique', 2, 'G1', 30),
        ('INFO202', 'Programmation Web',         teachers[0], 'Génie Informatique', 2, 'G1', 30),
        ('INFO203', 'Réseaux Informatiques',     teachers[1], 'Génie Informatique', 2, 'G1', 30),
        ('INFO204', 'Base de Données Avancées',  teachers[2], 'Génie Informatique', 2, 'G1', 30),
    ]

    modules = []
    for code, name, teacher, dept, yr, grp, hours in modules_data:
        mod, created = Module.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'teacher': teacher,
                'department': dept,
                'year_of_study': yr,
                'group': '',
                'total_hours': hours,
            }
        )
        modules.append(mod)
        if created:
            print(f"✅ Module créé: {code}")

    # ── SÉANCES ────────────────────────────────────────
    session_types = ['cours', 'td', 'tp']
    start_times = [time(8, 30), time(10, 30), time(14, 0), time(16, 0)]

    for mod in modules:
        for week in range(6):
            day_offset = week * 7 + random.randint(0, 4)
            session_date = date.today() - timedelta(days=day_offset)

            st = random.choice(start_times)
            et = time(st.hour + 2, st.minute)
            stype = random.choice(session_types)

            sess, created = Session.objects.get_or_create(
                module=mod,
                date=session_date,
                start_time=st,
                defaults={
                    'end_time': et,
                    'session_type': stype,
                    'room': f'Salle {random.randint(1,20):02d}',
                    'is_qr_active': False,
                }
            )

            if created:
                # Create attendance for enrolled students
                enrolled = StudentProfile.objects.filter(
                    year_of_study=mod.year_of_study,
                    department=mod.department
                )
                for student in enrolled:
                    # Random attendance: 80% present
                    rand = random.random()
                    if rand < 0.70:
                        status = 'present'
                    elif rand < 0.85:
                        status = 'absent'
                    elif rand < 0.95:
                        status = 'late'
                    else:
                        status = 'justified'

                    Attendance.objects.get_or_create(
                        student=student,
                        session=sess,
                        defaults={'status': status}
                    )

print("\n✅ Données de test créées avec succès!")
print("\n📋 Comptes disponibles:")
print("   admin / admin123    → Administrateur")
print("   prof1 / prof123     → Enseignant (Ahmed Benali)")
print("   prof2 / prof123     → Enseignant (Fatima Ezzahra)")
print("   etud1 / etud123     → Étudiant (Mohammed Alaoui)")
print("   etud2 / etud123     → Étudiant (Sara Tahiri)")
print("\n🌐 Accès: http://127.0.0.1:8000/")
