# academic/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Filiere, Niveau, Groupe, Salle, EmploiDuTemps
from accounts.models import TeacherProfile
from attendance.models import Module

def admin_required(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin():
            return redirect('dashboard:home')
        return func(request, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# ===== FILIERES =====
@login_required
@admin_required
def filiere_list(request):
    filieres = Filiere.objects.all()
    return render(request, 'academic/filiere_list.html', {'filieres': filieres})

@login_required
@admin_required
def filiere_create(request):
    if request.method == 'POST':
        Filiere.objects.create(name=request.POST.get('name'),
            code=request.POST.get('code'), description=request.POST.get('description',''))
        messages.success(request, 'Filiere creee.')
        return redirect('academic:filiere_list')
    return render(request, 'academic/filiere_form.html', {'action': 'Creer'})

@login_required
@admin_required
def filiere_edit(request, pk):
    filiere = get_object_or_404(Filiere, pk=pk)
    if request.method == 'POST':
        filiere.name = request.POST.get('name', filiere.name)
        filiere.code = request.POST.get('code', filiere.code)
        filiere.description = request.POST.get('description', filiere.description)
        filiere.is_active = 'is_active' in request.POST
        filiere.save()
        messages.success(request, 'Filiere modifiee.')
        return redirect('academic:filiere_list')
    return render(request, 'academic/filiere_form.html',
                  {'action': 'Modifier', 'filiere': filiere})

# ===== NIVEAUX =====
@login_required
@admin_required
def niveau_list(request):
    niveaux = Niveau.objects.select_related('filiere').all()
    filieres = Filiere.objects.filter(is_active=True)
    return render(request, 'academic/niveau_list.html',
                  {'niveaux': niveaux, 'filieres': filieres})

@login_required
@admin_required
def niveau_create(request):
    if request.method == 'POST':
        filiere = get_object_or_404(Filiere, pk=request.POST.get('filiere'))
        Niveau.objects.create(filiere=filiere, name=request.POST.get('name'),
            year_number=request.POST.get('year_number'),
            max_absence_percent=request.POST.get('max_absence_percent', 30))
        messages.success(request, 'Niveau cree.')
        return redirect('academic:niveau_list')
    filieres = Filiere.objects.filter(is_active=True)
    return render(request, 'academic/niveau_form.html', {'filieres': filieres, 'action': 'Creer'})

# ===== GROUPES =====
@login_required
@admin_required
def groupe_list(request):
    groupes = Groupe.objects.select_related('niveau__filiere').all()
    return render(request, 'academic/groupe_list.html', {'groupes': groupes})

@login_required
@admin_required
def groupe_create(request):
    if request.method == 'POST':
        niveau = get_object_or_404(Niveau, pk=request.POST.get('niveau'))
        Groupe.objects.create(niveau=niveau, name=request.POST.get('name'),
            max_students=request.POST.get('max_students', 30))
        messages.success(request, 'Groupe cree.')
        return redirect('academic:groupe_list')
    niveaux = Niveau.objects.select_related('filiere').all()
    return render(request, 'academic/groupe_form.html', {'niveaux': niveaux, 'action': 'Creer'})

# ===== SALLES =====
@login_required
@admin_required
def salle_list(request):
    salles = Salle.objects.all()
    return render(request, 'academic/salle_list.html', {'salles': salles})

@login_required
@admin_required
def salle_create(request):
    if request.method == 'POST':
        Salle.objects.create(name=request.POST.get('name'),
            capacity=request.POST.get('capacity', 30),
            room_type=request.POST.get('room_type', 'salle'),
            building=request.POST.get('building', ''),
            floor=request.POST.get('floor', ''))
        messages.success(request, 'Salle creee.')
        return redirect('academic:salle_list')
    return render(request, 'academic/salle_form.html', {'action': 'Creer'})

# ===== EMPLOI DU TEMPS =====
@login_required
@admin_required
def emploi_du_temps(request):
    selected_groupe = request.GET.get('groupe', '')
    groupes = Groupe.objects.select_related('niveau__filiere').filter(is_active=True)
    entries = EmploiDuTemps.objects.select_related('groupe','teacher__user','salle').filter(is_active=True)
    if selected_groupe:
        entries = entries.filter(groupe_id=selected_groupe)
    jours = ['lun','mar','mer','jeu','ven','sam']
    planning = {j: entries.filter(jour=j) for j in jours}
    return render(request, 'academic/emploi_du_temps.html', {
        'planning': planning, 'groupes': groupes, 'selected_groupe': selected_groupe,
        'jours_labels': ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi'],
    })

@login_required
@admin_required
def emploi_create(request):
    if request.method == 'POST':
        groupe_id = request.POST.get('groupe')
        teacher_id = request.POST.get('teacher')
        module_name = request.POST.get('module_name')
        session_type = request.POST.get('session_type', 'cours')
        semester = request.POST.get('semester', 1)

        # Créer l'entrée emploi du temps
        entry = EmploiDuTemps.objects.create(
            groupe_id=groupe_id,
            teacher_id=teacher_id,
            module_name=module_name,
            salle_id=request.POST.get('salle') or None,
            jour=request.POST.get('jour'),
            heure_debut=request.POST.get('heure_debut'),
            heure_fin=request.POST.get('heure_fin'),
            session_type=session_type,
            semester=semester
        )

        # Synchronisation — créer ou récupérer le Module dans attendance
        groupe = entry.groupe
        niveau = groupe.niveau
        teacher = entry.teacher

        module, created = Module.objects.get_or_create(
            teacher=teacher,
            code=f"{niveau.filiere.code}-{module_name[:10].upper().replace(' ','')}",
            defaults={
                'name': module_name,
                'department': niveau.filiere.name,
                'year_of_study': niveau.year_number,
                'semester': int(semester),
                'emploi_du_temps': entry,
            }
        )
        # Lier le module au groupe académique
        module.groupes.add(groupe)

        messages.success(request, f'Créneau ajouté et module "{module_name}" synchronisé.')
        return redirect('academic:emploi_du_temps')

    context = {
        'groupes': Groupe.objects.filter(is_active=True).select_related('niveau__filiere'),
        'teachers': TeacherProfile.objects.select_related('user').all(),
        'salles': Salle.objects.filter(is_active=True),
        'jours': EmploiDuTemps.JOURS,
        'types': [('cours','Cours'),('td','TD'),('tp','TP')],
    }
    return render(request, 'academic/emploi_form.html', context)