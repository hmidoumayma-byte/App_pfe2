from django.contrib import admin
from .models import Module, Session, Attendance, Justification


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'teacher', 'department', 'year_of_study', 'is_active']
    list_filter = ['department', 'year_of_study', 'is_active']
    search_fields = ['name', 'code']


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['module', 'date', 'start_time', 'end_time', 'session_type', 'is_qr_active']
    list_filter = ['session_type', 'is_qr_active', 'date']
    search_fields = ['module__name']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'status', 'scan_time']
    list_filter = ['status']
    search_fields = ['student__user__username']


@admin.register(Justification)
class JustificationAdmin(admin.ModelAdmin):
    list_display = ['student', 'reason', 'status', 'submitted_at']
    list_filter = ['status', 'reason']
