from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

# Code secret requis pour créer un compte Admin
ADMIN_SECRET_CODE = "MEDBOOKING2024"

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone = forms.CharField(required=False)
    role = forms.ChoiceField(choices=[
        ('patient', 'Patient'),
        ('doctor', 'Médecin / Doctor'),
        ('admin', 'Administrateur / Admin'),
    ])
    admin_code = forms.CharField(
        required=False,
        label="Code Admin (si rôle Admin)",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Requis uniquement pour le rôle Admin',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'role', 'admin_code', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['admin_code'].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        admin_code = cleaned_data.get('admin_code')
        if role == 'admin':
            if not admin_code:
                self.add_error('admin_code', "Le code secret est requis pour créer un compte Admin.")
            elif admin_code != ADMIN_SECRET_CODE:
                self.add_error('admin_code', "Code Admin incorrect.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if user.role == 'admin':
            user.is_staff = True
            user.is_superuser = True
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_pic', 'language']
        widgets = {f: forms.TextInput(attrs={'class': 'form-control'}) for f in ['first_name', 'last_name', 'email', 'phone']}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['language'].widget.attrs['class'] = 'form-select'
        self.fields['profile_pic'].widget.attrs['class'] = 'form-control'
