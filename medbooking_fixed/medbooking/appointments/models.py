from django.db import models
from accounts.models import User
from doctors.models import DoctorProfile

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    blood_type = models.CharField(max_length=5, blank=True)
    allergies = models.TextField(blank=True)
    chronic_conditions = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente / Pending'),
        ('confirmed', 'Confirmé / Confirmed'),
        ('cancelled', 'Annulé / Cancelled'),
        ('completed', 'Terminé / Completed'),
        ('no_show', 'Absent / No-show'),
    ]
    TYPE_CHOICES = [
        ('in_person', 'En cabinet / In-person'),
        ('online', 'En ligne / Online'),
    ]
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    appointment_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='in_person')
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="Doctor notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_appointments')
    cancel_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"{self.patient.get_full_name()} -> {self.doctor} on {self.date} at {self.start_time}"

class Notification(models.Model):
    TYPE_CHOICES = [
        ('appointment_confirmed', 'Appointment Confirmed'),
        ('appointment_cancelled', 'Appointment Cancelled'),
        ('appointment_reminder', 'Appointment Reminder'),
        ('appointment_completed', 'Appointment Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class WaitingList(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    preferred_date = models.DateField()
    preferred_time_from = models.TimeField()
    preferred_time_to = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_notified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.patient.get_full_name()} waiting for {self.doctor}"
