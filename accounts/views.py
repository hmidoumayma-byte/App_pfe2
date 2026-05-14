from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from .models import User, StudentProfile, TeacherProfile, PasswordResetToken
from .forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm, UserUpdateForm
from django.shortcuts import render

def home(request):
    if request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('dashboard:index')
    return render(request, 'home.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            remember_me = form.cleaned_data.get('remember_me', False)

            # Try login with username or email
            user = authenticate(request, username=username, password=password)
            if not user:
                # Try by email
                try:
                    u = User.objects.get(email=username)
                    user = authenticate(request, username=u.username, password=password)
                except User.DoesNotExist:
                    pass

            if user:
                if user.role != role:
                    messages.error(request, f'Ce compte n\'est pas un compte {dict(User.ROLE_CHOICES)[role]}.')
                elif not user.is_active:
                    messages.error(request, 'Votre compte est désactivé.')
                else:
                    login(request, user)
                    if not remember_me:
                        request.session.set_expiry(0)
                    messages.success(request, f'Bienvenue, {user.get_full_name() or user.username}!')
                    return redirect('dashboard:home')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data['role']
            user.phone = form.cleaned_data.get('phone', '')
            user.save()

            # Create profile based on role
            role = form.cleaned_data['role']
            department = form.cleaned_data.get('department', '')

            if role == 'student':
                from django.utils import timezone
                profile = StudentProfile.objects.create(
                    user=user,
                    student_id=form.cleaned_data['student_id'],
                    department=department,
                    year_of_study=form.cleaned_data.get('year_of_study', 1),
                    group=form.cleaned_data.get('group', ''),
                    institutional_code=form.cleaned_data.get('institutional_code', ''),
                    emergency_contact=form.cleaned_data.get('emergency_contact', ''),
                    terms_accepted=True,
                    terms_accepted_at=timezone.now(),
                )
                # Sauvegarder la photo si fournie
                if form.cleaned_data.get('identity_photo'):
                    profile.identity_photo = form.cleaned_data['identity_photo']
                    profile.save()

            elif role == 'teacher':
                TeacherProfile.objects.create(
                    user=user,
                    teacher_id=form.cleaned_data['teacher_id'],
                    department=department,
                    specialization=form.cleaned_data.get('specialization', ''),
                )

            messages.success(request, 'Compte créé avec succès! Vous pouvez maintenant vous connecter.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')

    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('accounts:login')


def forgot_password_view(request):
    form = ForgotPasswordForm()

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            token = get_random_string(64)
            PasswordResetToken.objects.create(user=user, token=token)

            reset_url = request.build_absolute_uri(f'/accounts/reset-password/{token}/')
            try:
                send_mail(
                    'Réinitialisation de votre mot de passe',
                    f'Cliquez sur ce lien pour réinitialiser votre mot de passe:\n{reset_url}\n\nCe lien expire dans 24 heures.',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
            except Exception:
                pass

            messages.success(request, 'Un email de réinitialisation a été envoyé. Vérifiez votre boîte mail.')
            return redirect('accounts:login')

    return render(request, 'accounts/forgot_password.html', {'form': form})


def reset_password_view(request, token):
    reset_token = get_object_or_404(PasswordResetToken, token=token)

    if not reset_token.is_valid():
        messages.error(request, 'Ce lien de réinitialisation est expiré ou déjà utilisé.')
        return redirect('accounts:forgot_password')

    form = ResetPasswordForm()

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = reset_token.user
            user.set_password(form.cleaned_data['password1'])
            user.save()
            reset_token.is_used = True
            reset_token.save()
            messages.success(request, 'Mot de passe réinitialisé avec succès!')
            return redirect('accounts:login')

    return render(request, 'accounts/reset_password.html', {'form': form, 'token': token})


@login_required
def profile_view(request):
    form = UserUpdateForm(instance=request.user)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès!')
            return redirect('accounts:profile')

    context = {'form': form}

    if request.user.is_student():
        try:
            context['profile'] = request.user.student_profile
        except StudentProfile.DoesNotExist:
            pass
    elif request.user.is_teacher():
        try:
            context['profile'] = request.user.teacher_profile
        except TeacherProfile.DoesNotExist:
            pass

    return render(request, 'accounts/profile.html', context)
