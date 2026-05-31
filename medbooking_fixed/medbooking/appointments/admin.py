from django.contrib import admin
from .models import Appointment, Notification, WaitingList, PatientProfile

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient','doctor','date','start_time','status','appointment_type']
    list_filter = ['status','appointment_type','date']
    search_fields = ['patient__username','doctor__user__username']

admin.site.register(PatientProfile)
admin.site.register(Notification)
admin.site.register(WaitingList)
