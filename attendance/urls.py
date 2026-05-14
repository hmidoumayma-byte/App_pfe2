from django.urls import path
from . import views
app_name = 'attendance'

urlpatterns = [
    # Teacher
    path('modules/', views.teacher_modules, name='teacher_modules'),
    path('modules/create/', views.create_module, name='create_module'),
    path('modules/<int:module_id>/absences/', views.module_absences, name='module_absences'),
    path('sessions/create/', views.create_session, name='create_session'),
    path('sessions/create/<int:module_id>/', views.create_session, name='create_session_for_module'),
    path('sessions/<int:pk>/', views.session_detail, name='session_detail'),
    path('sessions/<int:session_id>/qr/generate/', views.generate_qr, name='generate_qr'),
    path('sessions/<int:session_id>/qr/deactivate/', views.deactivate_qr, name='deactivate_qr'),
    path('sessions/<int:session_id>/attendance/mark/', views.mark_attendance_manual, name='mark_attendance'),

    # Student
    path('scan/<uuid:token>/', views.scan_qr, name='scan_qr'),
    path('my-absences/', views.student_absences, name='student_absences'),
    path('my-history/', views.student_history, name='student_history'),
    path('justify/<int:attendance_id>/', views.justify_absence, name='justify_absence'),

    # Admin
    path('admin/justifications/', views.admin_justifications, name='admin_justifications'),
    path('admin/justifications/<int:pk>/review/', views.review_justification, name='review_justification'),
    path('admin/absences/', views.admin_all_absences, name='admin_all_absences'),
    path('admin/students/<int:student_id>/', views.admin_student_detail, name='admin_student_detail'),
    path('admin/import-students/', views.import_students_excel, name='import_students'),
    path('admin/group-list/', views.admin_group_list, name='admin_group_list'),
    path('admin/import-students/', views.import_students_excel, name='import_students'),
    path('admin/download-template/', views.download_template, name='download_template'),
    path('admin/group-list/', views.admin_group_list, name='admin_group_list'),
    path('teacher/group-list/', views.teacher_group_list, name='teacher_group_list'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin/users/<int:user_id>/reset-password/', views.admin_reset_password, name='admin_reset_password'),
    path('teacher/statistics/', views.teacher_statistics, name='teacher_statistics'),
    path('student/planning/', views.student_planning, name='student_planning'),
    path('student/statistics/', views.student_statistics, name='student_statistics'),


]
