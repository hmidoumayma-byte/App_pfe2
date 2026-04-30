from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta, date
import json


@login_required
def home(request):
    user = request.user
    if user.is_admin():
        return admin_dashboard(request)
    elif user.is_teacher():
        return teacher_dashboard(request)
    elif user.is_student():
        return student_dashboard(request)
    return redirect('accounts:login')


@login_required
def admin_dashboard(request):
    from accounts.models import StudentProfile, TeacherProfile, User
    from attendance.models import Module, Session, Attendance, Justification
    from notifications.models import Notification

    total_students = StudentProfile.objects.count()
    total_teachers = TeacherProfile.objects.count()
    total_modules = Module.objects.filter(is_active=True).count()
    pending_justifications = Justification.objects.filter(status='pending').count()

    # Absence rate stats
    total_records = Attendance.objects.count()
    absent_records = Attendance.objects.filter(status='absent').count()
    global_absence_rate = round((absent_records / total_records * 100), 1) if total_records > 0 else 0

    # Students at risk (>30% absence)
    at_risk_students = []
    for student in StudentProfile.objects.select_related('user').all():
        total = Attendance.objects.filter(student=student).count()
        absent = Attendance.objects.filter(student=student, status='absent').count()
        if total > 0:
            pct = (absent / total) * 100
            if pct >= 30:
                at_risk_students.append({
                    'student': student,
                    'percentage': round(pct, 1),
                    'absent': absent,
                    'total': total,
                })
    at_risk_students.sort(key=lambda x: x['percentage'], reverse=True)

    # Recent sessions
    recent_sessions = Session.objects.select_related('module__teacher__user').order_by('-date', '-start_time')[:5]

    # Monthly absence data for chart
    monthly_data = []
    months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    for i in range(1, 13):
        count = Attendance.objects.filter(
            session__date__month=i,
            session__date__year=timezone.now().year,
            status='absent'
        ).count()
        monthly_data.append(count)

    # Recent notifications
    recent_notifs = Notification.objects.filter(is_read=False).order_by('-created_at')[:5]

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_modules': total_modules,
        'pending_justifications': pending_justifications,
        'global_absence_rate': global_absence_rate,
        'at_risk_students': at_risk_students[:10],
        'recent_sessions': recent_sessions,
        'monthly_data': json.dumps(monthly_data),
        'months': json.dumps(months),
        'recent_notifs': recent_notifs,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def teacher_dashboard(request):
    from attendance.models import Module, Session, Attendance

    try:
        teacher = request.user.teacher_profile
    except Exception:
        return render(request, 'dashboard/teacher_dashboard.html', {'error': True})

    modules = Module.objects.filter(teacher=teacher, is_active=True)
    total_sessions = Session.objects.filter(module__teacher=teacher).count()

    # Today's sessions
    today_sessions = Session.objects.filter(
        module__teacher=teacher,
        date=date.today()
    ).select_related('module')

    # Recent sessions
    recent_sessions = Session.objects.filter(
        module__teacher=teacher
    ).select_related('module').order_by('-date', '-start_time')[:5]

    # Module stats
    module_stats = []
    for module in modules:
        sessions_count = Session.objects.filter(module=module).count()
        total_att = Attendance.objects.filter(session__module=module).count()
        absent_att = Attendance.objects.filter(session__module=module, status='absent').count()
        absence_rate = round((absent_att / total_att * 100), 1) if total_att > 0 else 0
        module_stats.append({
            'module': module,
            'sessions': sessions_count,
            'absence_rate': absence_rate,
        })

    # Weekly attendance data for chart
    weekly_data = []
    labels = []
    for i in range(6, -1, -1):
        day = date.today() - timedelta(days=i)
        present = Attendance.objects.filter(
            session__module__teacher=teacher,
            session__date=day,
            status='present'
        ).count()
        absent = Attendance.objects.filter(
            session__module__teacher=teacher,
            session__date=day,
            status='absent'
        ).count()
        weekly_data.append({'present': present, 'absent': absent})
        labels.append(day.strftime('%a'))

    context = {
        'teacher': teacher,
        'modules': modules,
        'total_sessions': total_sessions,
        'today_sessions': today_sessions,
        'recent_sessions': recent_sessions,
        'module_stats': module_stats,
        'weekly_data': json.dumps(weekly_data),
        'labels': json.dumps(labels),
    }
    return render(request, 'dashboard/teacher_dashboard.html', context)


@login_required
def student_dashboard(request):
    from attendance.models import Module, Session, Attendance, Justification
    from notifications.models import Notification

    try:
        student = request.user.student_profile
    except Exception:
        return render(request, 'dashboard/student_dashboard.html', {'error': True})

    # Overall stats
    total_att = Attendance.objects.filter(student=student).count()
    present_att = Attendance.objects.filter(student=student, status='present').count()
    absent_att = Attendance.objects.filter(student=student, status='absent').count()
    justified_att = Attendance.objects.filter(student=student, status='justified').count()
    global_rate = round(((total_att - absent_att) / total_att * 100), 1) if total_att > 0 else 100

    # Module stats
    modules = Module.objects.filter(
        year_of_study=student.year_of_study,
        department=student.department
    )

    module_stats = []
    for module in modules:
        total = Session.objects.filter(module=module).count()
        absent = Attendance.objects.filter(student=student, session__module=module, status='absent').count()
        present = Attendance.objects.filter(student=student, session__module=module, status='present').count()
        percentage = round((absent / total * 100), 1) if total > 0 else 0
        module_stats.append({
            'module': module,
            'total': total,
            'present': present,
            'absent': absent,
            'percentage': percentage,
            'status': 'danger' if percentage >= 50 else ('warning' if percentage >= 30 else 'success'),
        })

    # Recent absences
    recent_absences = Attendance.objects.filter(
        student=student,
        status__in=['absent', 'late']
    ).select_related('session__module').order_by('-session__date')[:5]

    # Pending justifications
    pending_justifs = Justification.objects.filter(student=student, status='pending').count()

    # AI Predictions
    predictions = generate_student_predictions(student, module_stats)

    # Notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]

    # Attendance chart data
    chart_labels = [m['module'].code for m in module_stats]
    chart_rates = [m['percentage'] for m in module_stats]

    context = {
        'student': student,
        'total_att': total_att,
        'present_att': present_att,
        'absent_att': absent_att,
        'justified_att': justified_att,
        'global_rate': global_rate,
        'module_stats': module_stats,
        'recent_absences': recent_absences,
        'pending_justifs': pending_justifs,
        'predictions': predictions,
        'notifications': notifications,
        'chart_labels': json.dumps(chart_labels),
        'chart_rates': json.dumps(chart_rates),
    }
    return render(request, 'dashboard/student_dashboard.html', context)


def generate_student_predictions(student, module_stats):
    """AI-like prediction engine using rule-based logic + trend analysis."""
    from attendance.models import Attendance, Session
    predictions = []

    for stat in module_stats:
        module = stat['module']
        pct = stat['percentage']

        # Trend analysis: last 2 weeks vs previous 2 weeks
        recent_cutoff = date.today() - timedelta(days=14)
        older_cutoff = date.today() - timedelta(days=28)

        recent_absent = Attendance.objects.filter(
            student=student,
            session__module=module,
            session__date__gte=recent_cutoff,
            status='absent'
        ).count()

        older_absent = Attendance.objects.filter(
            student=student,
            session__module=module,
            session__date__gte=older_cutoff,
            session__date__lt=recent_cutoff,
            status='absent'
        ).count()

        trend = 'increasing' if recent_absent > older_absent else ('decreasing' if recent_absent < older_absent else 'stable')

        total_remaining_sessions = max(0, module.total_hours // 2 - stat['total'])

        if pct >= 50:
            predictions.append({
                'module': module,
                'level': 'critical',
                'icon': '🔴',
                'message': f"Taux d'absence critique ({pct}%)! Risque d'exclusion du module.",
                'recommendation': "Contactez immédiatement votre administration.",
                'trend': trend,
            })
        elif pct >= 30:
            max_allowed = int(stat['total'] * 0.33) - stat['absent']
            predictions.append({
                'module': module,
                'level': 'warning',
                'icon': '🟡',
                'message': f"Seuil d'alerte atteint ({pct}%). Tendance: {trend}.",
                'recommendation': f"Vous pouvez vous permettre max {max(0, max_allowed)} absences supplémentaires.",
                'trend': trend,
            })
        elif trend == 'increasing' and pct >= 15:
            predictions.append({
                'module': module,
                'level': 'info',
                'icon': '🔵',
                'message': f"Tendance d'absence en hausse dans {module.name}.",
                'recommendation': "Attention, votre taux d'absence augmente.",
                'trend': trend,
            })

    return predictions


@login_required
def ai_analysis(request):
    """Full AI analysis page."""
    from attendance.models import Attendance, Session, Module
    from accounts.models import StudentProfile

    user = request.user

    if user.is_student():
        try:
            student = user.student_profile
        except Exception:
            return redirect('dashboard:home')

        modules = Module.objects.filter(
            year_of_study=student.year_of_study,
            department=student.department
        )

        analysis_data = []
        for module in modules:
            total = Session.objects.filter(module=module).count()
            absent = Attendance.objects.filter(student=student, session__module=module, status='absent').count()
            present = Attendance.objects.filter(student=student, session__module=module, status='present').count()

            if total == 0:
                continue

            pct = round((absent / total) * 100, 1)

            # Weekly breakdown
            weekly = []
            for i in range(8):
                week_start = date.today() - timedelta(weeks=i+1)
                week_end = date.today() - timedelta(weeks=i)
                w_absent = Attendance.objects.filter(
                    student=student,
                    session__module=module,
                    session__date__gte=week_start,
                    session__date__lt=week_end,
                    status='absent'
                ).count()
                weekly.append(w_absent)
            weekly.reverse()

            # Predict future risk
            remaining = max(0, module.total_hours // 2 - total)
            if total > 0:
                future_absent = round(absent + (absent / total) * remaining)
                future_pct = round((future_absent / (total + remaining)) * 100, 1) if (total + remaining) > 0 else pct
            else:
                future_pct = 0

            analysis_data.append({
                'module': module,
                'total': total,
                'present': present,
                'absent': absent,
                'pct': pct,
                'weekly': json.dumps(weekly),
                'future_pct': future_pct,
                'risk': 'high' if future_pct >= 50 else ('medium' if future_pct >= 30 else 'low'),
            })

        return render(request, 'dashboard/ai_analysis.html', {
            'analysis_data': analysis_data,
            'student': student,
        })

    elif user.is_admin():
        # Admin: Global statistics & risk analysis
        all_students = StudentProfile.objects.select_related('user').all()
        risk_data = {'high': 0, 'medium': 0, 'low': 0}

        for student in all_students:
            total = Attendance.objects.filter(student=student).count()
            absent = Attendance.objects.filter(student=student, status='absent').count()
            if total > 0:
                pct = (absent / total) * 100
                if pct >= 50:
                    risk_data['high'] += 1
                elif pct >= 30:
                    risk_data['medium'] += 1
                else:
                    risk_data['low'] += 1

        return render(request, 'dashboard/ai_analysis_admin.html', {
            'risk_data': json.dumps(risk_data),
            'total_students': all_students.count(),
        })

    return redirect('dashboard:home')
