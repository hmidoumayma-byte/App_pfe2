from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm
from django.core.exceptions import ValidationError
from .models import User, StudentProfile, TeacherProfile


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Nom d\'utilisateur',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur ou email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        label='Rôle',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    remember_me = forms.BooleanField(required=False, label='Se souvenir de moi')


class RegisterForm(UserCreationForm):
    ROLE_CHOICES = [
        ('student', 'Étudiant'),
        ('teacher', 'Enseignant'),
    ]

    first_name = forms.CharField(
        label='Prénom',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'})
    )
    last_name = forms.CharField(
        label='Nom',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label='Rôle',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    phone = forms.CharField(
        label='Téléphone',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'})
    )

    # Student fields
    student_id = forms.CharField(
        label='Numéro Étudiant',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: ETU20240001'})
    )
    year_of_study = forms.ChoiceField(
        choices=[(i, f'{i}ème Année') for i in range(1, 6)],
        required=False,
        label='Année d\'étude',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    group = forms.CharField(
        label='Groupe',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: G1'})
    )

    # Teacher fields
    teacher_id = forms.CharField(
        label='Numéro Enseignant',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: ENS2024001'})
    )
    specialization = forms.CharField(
        label='Spécialisation',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Génie Logiciel'})
    )

    department = forms.CharField(
        label='Département',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Génie Informatique'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})
        self.fields['password1'].label = 'Mot de passe'
        self.fields['password2'].label = 'Confirmer mot de passe'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')

        if role == 'student':
            if not cleaned_data.get('student_id'):
                self.add_error('student_id', 'Le numéro étudiant est requis.')
            else:
                from accounts.models import StudentProfile
                if StudentProfile.objects.filter(student_id=cleaned_data.get('student_id')).exists():
                    self.add_error('student_id', ' Ce numéro étudiant existe déjà.')
            if not cleaned_data.get('department'):
                self.add_error('department', 'Le département est requis.')

        elif role == 'teacher':
            if not cleaned_data.get('teacher_id'):
                self.add_error('teacher_id', 'Le numéro enseignant est requis.')
            else:
                from accounts.models import TeacherProfile
                if TeacherProfile.objects.filter(teacher_id=cleaned_data.get('teacher_id')).exists():
                    self.add_error('teacher_id', 'Ce numéro enseignant existe déjà.')
            if not cleaned_data.get('department'):
                self.add_error('department', 'Le département est requis.')

        return cleaned_data


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre adresse email'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError("Aucun compte associé à cet email.")
        return email


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(
        label='Nouveau mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nouveau mot de passe'})
    )
    password2 = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
