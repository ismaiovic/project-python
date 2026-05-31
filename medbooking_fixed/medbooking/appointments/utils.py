from django.core.mail import send_mail
from django.utils.translation import gettext as _
from django.conf import settings
from .models import Notification

def send_appointment_email(appointment, event_type):
    patient = appointment.patient
    doctor = appointment.doctor
    subject_map = {
        'confirmed': f'Rendez-vous confirmé / Appointment Confirmed - {appointment.date}',
        'cancelled': f'Rendez-vous annulé / Appointment Cancelled - {appointment.date}',
        'completed': f'Consultation terminée / Consultation Completed - {appointment.date}',
    }
    body_map = {
        'confirmed': f"""Bonjour {patient.get_full_name()} / Hello {patient.get_full_name()},

FR: Votre rendez-vous avec Dr. {doctor.user.get_full_name()} est confirmé.
EN: Your appointment with Dr. {doctor.user.get_full_name()} is confirmed.

Date: {appointment.date}
Heure / Time: {appointment.start_time}
Type: {appointment.get_appointment_type_display()}

MedBooking Team""",
        'cancelled': f"""Bonjour {patient.get_full_name()} / Hello {patient.get_full_name()},

FR: Votre rendez-vous du {appointment.date} avec Dr. {doctor.user.get_full_name()} a été annulé.
EN: Your appointment on {appointment.date} with Dr. {doctor.user.get_full_name()} has been cancelled.

MedBooking Team""",
        'completed': f"""Bonjour {patient.get_full_name()} / Hello {patient.get_full_name()},

FR: Merci pour votre consultation. N'hésitez pas à laisser un avis.
EN: Thank you for your consultation. Feel free to leave a review.

MedBooking Team""",
    }
    subject = subject_map.get(event_type, 'MedBooking Notification')
    body = body_map.get(event_type, '')
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [patient.email], fail_silently=True)
    except Exception:
        pass

def create_notification(user, notif_type, appointment, message):
    Notification.objects.create(user=user, notif_type=notif_type, appointment=appointment, message=message)
