from django import forms
from .models import Module, Session, Justification


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['name', 'code', 'department', 'year_of_study', 'group', 'total_hours', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du module'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: INFO301'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Génie Informatique'}),
            'year_of_study': forms.Select(
                choices=[(i, f'{i}ème Année') for i in range(1, 6)],
                attrs={'class': 'form-select'}
            ),
            'group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: G1 (optionnel)'}),
            'total_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['module', 'date', 'start_time', 'end_time', 'session_type', 'room', 'notes']
        widgets = {
            'module': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'session_type': forms.Select(attrs={'class': 'form-select'}),
            'room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Salle A12'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['module'].queryset = Module.objects.filter(teacher=teacher, is_active=True)


class JustificationForm(forms.ModelForm):
    class Meta:
        model = Justification
        fields = ['reason', 'description', 'document']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez la raison de votre absence...'
            }),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'reason': 'Raison',
            'description': 'Description',
            'document': 'Document justificatif (optionnel)',
        }


class ManualAttendanceForm(forms.Form):
    STATUS_CHOICES = [
        ('present', 'Présent'),
        ('absent', 'Absent'),
        ('late', 'En retard'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-select form-select-sm'}))
