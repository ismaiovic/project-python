from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

def home(request):
    from doctors.models import DoctorProfile, Specialty
    doctors = DoctorProfile.objects.select_related('user','specialty')[:6]
    specialties = Specialty.objects.all()
    return render(request, 'home.html', {'doctors': doctors, 'specialties': specialties})

def dashboard_redirect(request):
    from accounts.views import dashboard_view
    return dashboard_view(request)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', home, name='home'),
    path('dashboard/', dashboard_redirect, name='dashboard'),
    path('accounts/', include('accounts.urls')),
    path('doctors/', include('doctors.urls')),
    path('appointments/', include('appointments.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
