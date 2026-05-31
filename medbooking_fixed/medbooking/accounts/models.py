from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Médecin / Doctor'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=20, blank=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)
    language = models.CharField(max_length=5, choices=[('fr','Français'),('en','English')], default='fr')

    def is_patient(self):
        return self.role == 'patient'
    def is_doctor(self):
        return self.role == 'doctor'
    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser
