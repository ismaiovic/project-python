from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .models import DoctorProfile, Specialty, Availability, Review
from .forms import DoctorProfileForm, AvailabilityForm, ReviewForm

def doctor_list(request):
    doctors = DoctorProfile.objects.select_related('user','specialty').all()
    specialties = Specialty.objects.all()
    q = request.GET.get('q','')
    specialty_id = request.GET.get('specialty','')
    city = request.GET.get('city','')
    online = request.GET.get('online','')
    if q:
        doctors = doctors.filter(Q(user__first_name__icontains=q)|Q(user__last_name__icontains=q)|Q(specialty__name_fr__icontains=q)|Q(specialty__name_en__icontains=q))
    if specialty_id:
        doctors = doctors.filter(specialty_id=specialty_id)
    if city:
        doctors = doctors.filter(city__icontains=city)
    if online:
        doctors = doctors.filter(is_available_online=True)
    return render(request, 'doctors/list.html', {'doctors': doctors, 'specialties': specialties, 'q': q})

def doctor_detail(request, pk):
    doctor = get_object_or_404(DoctorProfile, pk=pk)
    availabilities = doctor.availabilities.filter(is_active=True)
    reviews = doctor.reviews.all()[:10]
    can_review = False
    if request.user.is_authenticated and request.user.is_patient():
        from appointments.models import Appointment
        can_review = Appointment.objects.filter(patient=request.user, doctor=doctor, status='completed').exists()
        already_reviewed = Review.objects.filter(doctor=doctor, patient=request.user).exists()
        can_review = can_review and not already_reviewed
    review_form = ReviewForm() if can_review else None
    return render(request, 'doctors/detail.html', {'doctor': doctor, 'availabilities': availabilities, 'reviews': reviews, 'review_form': review_form, 'can_review': can_review})

@login_required
def submit_review(request, pk):
    doctor = get_object_or_404(DoctorProfile, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.doctor = doctor
            review.patient = request.user
            review.save()
            # Update doctor rating
            reviews = doctor.reviews.all()
            avg = sum(r.rating for r in reviews) / reviews.count()
            doctor.rating = round(avg, 2)
            doctor.rating_count = reviews.count()
            doctor.save()
            messages.success(request, _('Review submitted successfully.'))
    return redirect('doctor_detail', pk=pk)

@login_required
def my_profile(request):
    if not request.user.is_doctor():
        return redirect('dashboard')
    try:
        profile = request.user.doctor_profile
    except DoctorProfile.DoesNotExist:
        profile = DoctorProfile.objects.create(user=request.user)
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Profile updated.'))
            return redirect('doctor_my_profile')
    else:
        form = DoctorProfileForm(instance=profile)
    return render(request, 'doctors/my_profile.html', {'form': form, 'profile': profile})

@login_required
def manage_availability(request):
    if not request.user.is_doctor():
        return redirect('dashboard')
    profile = request.user.doctor_profile
    availabilities = profile.availabilities.all()
    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            av = form.save(commit=False)
            av.doctor = profile
            av.save()
            messages.success(request, _('Availability added.'))
            return redirect('manage_availability')
    else:
        form = AvailabilityForm()
    return render(request, 'doctors/availability.html', {'form': form, 'availabilities': availabilities})

@login_required
def delete_availability(request, pk):
    av = get_object_or_404(Availability, pk=pk, doctor=request.user.doctor_profile)
    av.delete()
    messages.success(request, _('Availability removed.'))
    return redirect('manage_availability')
