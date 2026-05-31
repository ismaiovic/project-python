import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medbooking.settings')
django.setup()

from accounts.models import User
from doctors.models import Specialty, DoctorProfile, Availability
from appointments.models import PatientProfile

# Specialties
specialties_data = [
    ('Cardiologie', 'Cardiology', 'fas fa-heart'),
    ('Pédiatrie', 'Pediatrics', 'fas fa-baby'),
    ('Dermatologie', 'Dermatology', 'fas fa-hand-sparkles'),
    ('Neurologie', 'Neurology', 'fas fa-brain'),
    ('Orthopédie', 'Orthopedics', 'fas fa-bone'),
    ('Ophtalmologie', 'Ophthalmology', 'fas fa-eye'),
    ('Médecine générale', 'General Medicine', 'fas fa-stethoscope'),
    ('Gynécologie', 'Gynecology', 'fas fa-venus'),
]
for name_fr, name_en, icon in specialties_data:
    Specialty.objects.get_or_create(name_fr=name_fr, defaults={'name_en': name_en, 'icon': icon})

print("Specialties created")

# Admin user
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@medbooking.com', 'admin123', role='admin', first_name='Admin', last_name='MedBooking')
    print("Admin: admin / admin123")

# Doctors
doctors_data = [
    ('dr.dupont', 'Jean', 'Dupont', 'jean.dupont@med.com', 'Cardiologie', 'Casablanca', True),
    ('dr.benali', 'Fatima', 'Benali', 'fatima.benali@med.com', 'Pédiatrie', 'Rabat', False),
    ('dr.martin', 'Pierre', 'Martin', 'pierre.martin@med.com', 'Neurologie', 'Casablanca', True),
]
for username, first, last, email, spec, city, online in doctors_data:
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username, email, 'doctor123', first_name=first, last_name=last, role='doctor')
        specialty = Specialty.objects.get(name_fr=spec)
        profile = DoctorProfile.objects.create(user=user, specialty=specialty, city=city, is_available_online=online, experience_years=10, consultation_fee=300)
        # Add availability Mon-Fri 9:00-17:00
        for day in range(5):
            Availability.objects.create(doctor=profile, day_of_week=day, start_time='09:00', end_time='17:00', slot_duration=30)
        print(f"Doctor: {username} / doctor123")

# Patient
if not User.objects.filter(username='patient1').exists():
    patient = User.objects.create_user('patient1', 'patient@test.com', 'patient123', first_name='Mohamed', last_name='Alaoui', role='patient')
    PatientProfile.objects.create(user=patient, blood_type='A+')
    print("Patient: patient1 / patient123")

print("\nDone! Seed data created successfully.")
