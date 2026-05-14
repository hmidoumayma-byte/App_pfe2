# core_settings/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SystemSettings, ActionLog

def admin_required(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin():
            return redirect('dashboard:home')
        return func(request, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@login_required
@admin_required
def system_settings(request):
    s = SystemSettings.get_settings()
    if request.method == 'POST':
        s.institution_name = request.POST.get('institution_name', '')
        s.institution_address = request.POST.get('institution_address', '')
        s.institution_phone = request.POST.get('institution_phone', '')
        s.institution_email = request.POST.get('institution_email', '')
        s.academic_year = request.POST.get('academic_year', '')
        s.alert_threshold = float(request.POST.get('alert_threshold', 30))
        s.critical_threshold = float(request.POST.get('critical_threshold', 50))
        s.justification_deadline_days = int(request.POST.get('deadline', 7))
        s.allow_student_register = 'allow_register' in request.POST
        s.updated_by = request.user
        if request.FILES.get('institution_logo'):
            s.institution_logo = request.FILES['institution_logo']
        s.save()
        ActionLog.objects.create(user=request.user, action='update_settings',
            description='Modification parametres systeme',
            ip_address=request.META.get('REMOTE_ADDR'))
        messages.success(request, 'Parametres sauvegardes.')
        return redirect('core_settings:settings')
    return render(request, 'core_settings/settings.html', {'s': s})

@login_required
@admin_required
def action_logs(request):
    logs = ActionLog.objects.select_related('user').all()[:200]
    return render(request, 'core_settings/logs.html', {'logs': logs})

@login_required
@admin_required
def backup_data(request):
    import json
    from django.http import HttpResponse
    from accounts.models import StudentProfile, TeacherProfile
    from attendance.models import Attendance, Module, Session
    data = {
        'students': list(StudentProfile.objects.values()),
        'teachers': list(TeacherProfile.objects.values()),
        'modules':  list(Module.objects.values()),
        'sessions': list(Session.objects.values()),
        'absences': list(Attendance.objects.values()),
    }
    response = HttpResponse(json.dumps(data, default=str, indent=2), content_type='application/json')
    from django.utils import timezone
    ts = timezone.now().strftime('%Y%m%d_%H%M')
    response['Content-Disposition'] = f'attachment; filename=backup_{ts}.json'
    return response
