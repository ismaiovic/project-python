from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.db.models import Count
import datetime, json
from .models import Appointment, Notification, WaitingList, PatientProfile
from .forms import AppointmentForm, AppointmentUpdateForm, CancelForm, WaitingListForm
from doctors.models import DoctorProfile
from .utils import send_appointment_email, create_notification

@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, pk=doctor_id)
    if not request.user.is_patient():
        messages.error(request, _('Only patients can book appointments.'))
        return redirect('doctor_detail', pk=doctor_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            apt = form.save(commit=False)
            apt.patient = request.user
            apt.doctor = doctor
            # Calculate end time (30 min default)
            start = datetime.datetime.combine(apt.date, apt.start_time)
            apt.end_time = (start + datetime.timedelta(minutes=30)).time()
            # Check conflicts
            conflict = Appointment.objects.filter(
                doctor=doctor, date=apt.date, status__in=['pending','confirmed'],
                start_time__lt=apt.end_time, end_time__gt=apt.start_time
            ).exists()
            if conflict:
                messages.error(request, _('This time slot is already taken. Please choose another.'))
            else:
                apt.status = 'pending'
                apt.save()
                send_appointment_email(apt, 'confirmed')
                create_notification(request.user, 'appointment_confirmed', apt,
                    f'Appointment with Dr. {doctor.user.get_full_name()} on {apt.date} at {apt.start_time}')
                messages.success(request, _('Appointment booked successfully! Confirmation sent to your email.'))
                return redirect('my_appointments')
    else:
        form = AppointmentForm()
    return render(request, 'appointments/book.html', {'form': form, 'doctor': doctor})

@login_required
def my_appointments(request):
    user = request.user
    if user.is_patient():
        appointments = Appointment.objects.filter(patient=user).select_related('doctor__user','doctor__specialty')
    elif user.is_doctor():
        appointments = Appointment.objects.filter(doctor=user.doctor_profile).select_related('patient')
    else:
        appointments = Appointment.objects.all().select_related('patient','doctor__user')
    status_filter = request.GET.get('status','')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    return render(request, 'appointments/list.html', {'appointments': appointments, 'status_filter': status_filter})

@login_required
def appointment_detail(request, pk):
    apt = get_object_or_404(Appointment, pk=pk)
    user = request.user
    if not (user == apt.patient or (user.is_doctor() and apt.doctor == user.doctor_profile) or user.is_admin_user()):
        messages.error(request, _('Access denied.'))
        return redirect('my_appointments')
    update_form = None
    if user.is_doctor() and apt.doctor == user.doctor_profile:
        if request.method == 'POST' and 'update' in request.POST:
            update_form = AppointmentUpdateForm(request.POST, instance=apt)
            if update_form.is_valid():
                update_form.save()
                messages.success(request, _('Appointment updated.'))
                return redirect('appointment_detail', pk=pk)
        else:
            update_form = AppointmentUpdateForm(instance=apt)
    return render(request, 'appointments/detail.html', {'apt': apt, 'update_form': update_form})

@login_required
def cancel_appointment(request, pk):
    apt = get_object_or_404(Appointment, pk=pk)
    user = request.user
    if not (user == apt.patient or (user.is_doctor() and apt.doctor == user.doctor_profile) or user.is_admin_user()):
        messages.error(request, _('Access denied.'))
        return redirect('my_appointments')
    if request.method == 'POST':
        form = CancelForm(request.POST)
        if form.is_valid():
            apt.status = 'cancelled'
            apt.cancelled_by = user
            apt.cancel_reason = form.cleaned_data.get('reason','')
            apt.save()
            send_appointment_email(apt, 'cancelled')
            create_notification(apt.patient, 'appointment_cancelled', apt,
                f'Appointment on {apt.date} has been cancelled.')
            messages.success(request, _('Appointment cancelled.'))
            return redirect('my_appointments')
    else:
        form = CancelForm()
    return render(request, 'appointments/cancel.html', {'apt': apt, 'form': form})

@login_required
def notifications_view(request):
    notifs = request.user.notifications.all()
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'appointments/notifications.html', {'notifications': notifs})

@login_required
def medical_history(request):
    if not request.user.is_patient():
        return redirect('dashboard')
    appointments = Appointment.objects.filter(patient=request.user, status='completed').select_related('doctor__user','doctor__specialty')
    try:
        profile = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        profile = None
    return render(request, 'appointments/history.html', {'appointments': appointments, 'profile': profile})

@login_required
def statistics_view(request):
    if not (request.user.is_admin_user() or request.user.is_doctor()):
        return redirect('dashboard')
    if request.user.is_doctor():
        qs = Appointment.objects.filter(doctor=request.user.doctor_profile)
    else:
        qs = Appointment.objects.all()
    by_status = list(qs.values('status').annotate(count=Count('id')))
    by_month = list(qs.extra(select={'month': "strftime('%Y-%m', date)"}).values('month').annotate(count=Count('id')).order_by('month')[:12])
    return render(request, 'appointments/statistics.html', {
        'by_status': json.dumps(by_status),
        'by_month': json.dumps(by_month),
        'total': qs.count(),
        'completed': qs.filter(status='completed').count(),
        'pending': qs.filter(status='pending').count(),
        'cancelled': qs.filter(status='cancelled').count(),
    })

@login_required
def api_available_slots(request, doctor_id):
    """AJAX: return available slots for a given doctor + date"""
    doctor = get_object_or_404(DoctorProfile, pk=doctor_id)
    date_str = request.GET.get('date','')
    try:
        date = datetime.date.fromisoformat(date_str)
    except ValueError:
        return JsonResponse({'slots': []})
    day_of_week = date.weekday()
    availabilities = doctor.availabilities.filter(day_of_week=day_of_week, is_active=True)
    booked = list(Appointment.objects.filter(doctor=doctor, date=date, status__in=['pending','confirmed']).values_list('start_time', flat=True))
    slots = []
    for av in availabilities:
        current = datetime.datetime.combine(date, av.start_time)
        end = datetime.datetime.combine(date, av.end_time)
        while current + datetime.timedelta(minutes=av.slot_duration) <= end:
            if current.time() not in booked:
                slots.append(current.strftime('%H:%M'))
            current += datetime.timedelta(minutes=av.slot_duration)
    return JsonResponse({'slots': slots})
