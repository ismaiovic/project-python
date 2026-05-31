from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import RegisterForm, LoginForm, UserUpdateForm
from .models import User
from doctors.models import DoctorProfile, Specialty
from appointments.models import PatientProfile

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == 'doctor':
                DoctorProfile.objects.create(user=user)
            else:
                PatientProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, _('Account created successfully! Welcome to MedBooking.'))
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, _('Welcome back, %(name)s!') % {'name': user.first_name or user.username})
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            messages.error(request, _('Invalid credentials. Please try again.'))
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, _('You have been logged out.'))
    return redirect('home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Profile updated successfully.'))
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def dashboard_view(request):
    user = request.user
    context = {'user': user}
    if user.is_patient():
        from appointments.models import Appointment
        upcoming = Appointment.objects.filter(patient=user, status__in=['pending','confirmed']).order_by('date','start_time')[:5]
        past = Appointment.objects.filter(patient=user, status__in=['completed','cancelled']).order_by('-date')[:5]
        context.update({'upcoming': upcoming, 'past': past, 'total': Appointment.objects.filter(patient=user).count()})
    elif user.is_doctor():
        try:
            profile = user.doctor_profile
            from appointments.models import Appointment
            today_appts = Appointment.objects.filter(doctor=profile, status__in=['pending','confirmed']).order_by('date','start_time')[:10]
            context.update({'profile': profile, 'today_appts': today_appts,
                'total_patients': Appointment.objects.filter(doctor=profile).values('patient').distinct().count(),
                'pending_count': Appointment.objects.filter(doctor=profile, status='pending').count()})
        except DoctorProfile.DoesNotExist:
            pass
    elif user.is_admin_user():
        from appointments.models import Appointment
        context.update({
            'total_users': User.objects.count(),
            'total_doctors': User.objects.filter(role='doctor').count(),
            'total_patients': User.objects.filter(role='patient').count(),
            'total_appointments': Appointment.objects.count(),
            'recent_appointments': Appointment.objects.order_by('-created_at')[:10],
        })
    return render(request, 'accounts/dashboard.html', context)
