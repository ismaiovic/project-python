from django.contrib import admin
from .models import Specialty, DoctorProfile, Availability, Review

admin.site.register(Specialty)
admin.site.register(DoctorProfile)
admin.site.register(Availability)
admin.site.register(Review)
