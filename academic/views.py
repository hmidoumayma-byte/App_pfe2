# academic/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
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
        Filiere.objects.create(
            name=request.POST.get('name'),
            code=request.POST.get('code'),
            description=request.POST.get('description', '')
        )
        messages.success(request, 'Filière créée avec succès.')
        return redirect('academic:filiere_list')
    return render(request, 'academic/filiere_form.html', {'action': 'Créer'})


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
        messages.success(request, 'Filière modifiée.')
        return redirect('academic:filiere_list')
    return render(request, 'academic/filiere_form.html', {'action': 'Modifier', 'filiere': filiere})


# ===== NIVEAUX =====

@login_required
@admin_required
def niveau_list(request):
    niveaux = Niveau.objects.select_related('filiere').all()
    filieres = Filiere.objects.filter(is_active=True)
    return render(request, 'academic/niveau_list.html', {'niveaux': niveaux, 'filieres': filieres})


@login_required
@admin_required
def niveau_create(request):
    if request.method == 'POST':
        filiere = get_object_or_404(Filiere, pk=request.POST.get('filiere'))
        year_number = request.POST.get('year_number')
        
        # Vérifier si ce niveau existe déjà avant de créer
        if Niveau.objects.filter(filiere=filiere, year_number=year_number).exists():
            messages.error(request, f'Ce niveau (Année {year_number}) existe déjà pour la filière {filiere.name}.')
            filieres = Filiere.objects.filter(is_active=True)
            return render(request, 'academic/niveau_form.html', {
                'filieres': filieres, 'action': 'Créer'
            })
        
        Niveau.objects.create(
            filiere=filiere,
            name=request.POST.get('name'),
            year_number=year_number,
            max_absence_percent=request.POST.get('max_absence_percent', 30)
        )
        messages.success(request, 'Niveau créé.')
        return redirect('academic:niveau_list')
    filieres = Filiere.objects.filter(is_active=True)
    return render(request, 'academic/niveau_form.html', {'filieres': filieres, 'action': 'Créer'})

@login_required
@admin_required
def niveau_edit(request, pk):
    niveau = get_object_or_404(Niveau, pk=pk)
    if request.method == 'POST':
        niveau.name = request.POST.get('name', niveau.name)
        niveau.year_number = request.POST.get('year_number', niveau.year_number)
        niveau.max_absence_percent = request.POST.get('max_absence_percent', niveau.max_absence_percent)
        niveau.save()
        messages.success(request, 'Niveau modifié.')
        return redirect('academic:niveau_list')
    filieres = Filiere.objects.filter(is_active=True)
    return render(request, 'academic/niveau_form.html', {
        'filieres': filieres, 'action': 'Modifier', 'niveau': niveau
    })


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
        Groupe.objects.create(
            niveau=niveau,
            name=request.POST.get('name'),
            max_students=request.POST.get('max_students', 30)
        )
        messages.success(request, 'Groupe créé.')
        return redirect('academic:groupe_list')
    niveaux = Niveau.objects.select_related('filiere').all()
    return render(request, 'academic/groupe_form.html', {'niveaux': niveaux, 'action': 'Créer'})


@login_required
@admin_required
def groupe_edit(request, pk):
    groupe = get_object_or_404(Groupe, pk=pk)
    if request.method == 'POST':
        groupe.name = request.POST.get('name', groupe.name)
        groupe.max_students = request.POST.get('max_students', groupe.max_students)
        groupe.is_active = 'is_active' in request.POST
        groupe.save()
        messages.success(request, 'Groupe modifié.')
        return redirect('academic:groupe_list')
    niveaux = Niveau.objects.select_related('filiere').all()
    return render(request, 'academic/groupe_form.html', {
        'niveaux': niveaux, 'action': 'Modifier', 'groupe': groupe
    })


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
        Salle.objects.create(
            name=request.POST.get('name'),
            capacity=request.POST.get('capacity', 30),
            room_type=request.POST.get('room_type', 'salle'),
            building=request.POST.get('building', ''),
            floor=request.POST.get('floor', '')
        )
        messages.success(request, 'Salle créée.')
        return redirect('academic:salle_list')
    return render(request, 'academic/salle_form.html', {'action': 'Créer'})


@login_required
@admin_required
def salle_edit(request, pk):
    salle = get_object_or_404(Salle, pk=pk)
    if request.method == 'POST':
        salle.name = request.POST.get('name', salle.name)
        salle.capacity = request.POST.get('capacity', salle.capacity)
        salle.room_type = request.POST.get('room_type', salle.room_type)
        salle.building = request.POST.get('building', salle.building)
        salle.floor = request.POST.get('floor', salle.floor)
        salle.is_active = 'is_active' in request.POST
        salle.save()
        messages.success(request, 'Salle modifiée.')
        return redirect('academic:salle_list')
    return render(request, 'academic/salle_form.html', {'action': 'Modifier', 'salle': salle})


# ===== EMPLOI DU TEMPS =====

@login_required
@admin_required
def emploi_du_temps(request):
    selected_groupe = request.GET.get('groupe', '')
    groupes = Groupe.objects.select_related('niveau__filiere').filter(is_active=True)
    entries = EmploiDuTemps.objects.select_related(
        'groupe__niveau__filiere', 'teacher__user', 'salle'
    ).filter(is_active=True)
    if selected_groupe:
        entries = entries.filter(groupe_id=selected_groupe)
    jours = ['lun', 'mar', 'mer', 'jeu', 'ven', 'sam']
    planning = {j: list(entries.filter(jour=j)) for j in jours}
    return render(request, 'academic/emploi_du_temps.html', {
        'planning': planning,
        'groupes': groupes,
        'selected_groupe': selected_groupe,
        'jours_labels': ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'],
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
            semester=int(semester)
        )

        # ── SYNCHRONISATION AUTOMATIQUE ──
        # Créer ou récupérer le Module correspondant dans l'app attendance
        groupe = entry.groupe
        niveau = groupe.niveau
        teacher = entry.teacher

        code_module = f"{niveau.filiere.code}-{module_name[:10].upper().replace(' ', '').replace('-', '')}"

        module, created = Module.objects.get_or_create(
            teacher=teacher,
            code=code_module,
            defaults={
                'name': module_name,
                'department': niveau.filiere.name,
                'year_of_study': niveau.year_number,
                # ← PAS de champ 'semester' ici — il n'existe pas dans le modèle Module
                'emploi_du_temps': entry,
            }
        )

        # Lier le module au groupe académique
        module.groupes.add(groupe)

        if created:
            messages.success(request, f'Créneau ajouté. Module "{module_name}" créé et synchronisé pour {teacher.user.get_full_name()}.')
        else:
            messages.success(request, f'Créneau ajouté. Module "{module_name}" existant lié au groupe {groupe}.')

        return redirect('academic:emploi_du_temps')

    context = {
        'groupes': Groupe.objects.filter(is_active=True).select_related('niveau__filiere'),
        'teachers': TeacherProfile.objects.select_related('user').all(),
        'salles': Salle.objects.filter(is_active=True),
        'jours': EmploiDuTemps.JOURS,
        'types': [('cours', 'Cours'), ('td', 'TD'), ('tp', 'TP')],
        'semestres': [(1, 'Semestre 1'), (2, 'Semestre 2')],
    }
    return render(request, 'academic/emploi_form.html', context)


@login_required
@admin_required
def emploi_delete(request, pk):
    entry = get_object_or_404(EmploiDuTemps, pk=pk)
    if request.method == 'POST':
        entry.is_active = False
        entry.save()
        messages.success(request, 'Créneau supprimé.')
    return redirect('academic:emploi_du_temps')


# ===== API JSON (pour les selects dynamiques) =====

from django.http import JsonResponse

def api_niveaux_by_filiere(request, filiere_id):
    """Retourne les niveaux d'une filière en JSON — sans @login_required (formulaire public)."""
    # ✅ Niveau n'a PAS de champ is_active — on filtre uniquement par filiere_id
    niveaux = Niveau.objects.filter(
        filiere_id=filiere_id
    ).order_by('year_number').values('id', 'name', 'year_number')
    return JsonResponse({'niveaux': list(niveaux)})


def api_groupes_by_niveau(request, niveau_id):
    """Retourne les groupes d'un niveau en JSON — sans @login_required (formulaire public)."""
    # ✅ Groupe a bien is_active — on l'utilise uniquement ici
    groupes = Groupe.objects.filter(
        niveau_id=niveau_id, is_active=True
    ).order_by('name').values('id', 'name', 'max_students')
    return JsonResponse({'groupes': list(groupes)})