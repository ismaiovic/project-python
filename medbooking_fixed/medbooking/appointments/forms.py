from django import forms
from .models import Appointment, WaitingList
from doctors.models import DoctorProfile
import datetime

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date','start_time','appointment_type','reason']
        widgets = {
            'date': forms.DateInput(attrs={'type':'date','class':'form-control','min': str(datetime.date.today())}),
            'start_time': forms.TimeInput(attrs={'type':'time','class':'form-control'}),
            'appointment_type': forms.Select(attrs={'class':'form-select'}),
            'reason': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }

class AppointmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status','notes']
        widgets = {
            'status': forms.Select(attrs={'class':'form-select'}),
            'notes': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }

class CancelForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control','rows':3}), required=False)

class WaitingListForm(forms.ModelForm):
    class Meta:
        model = WaitingList
        fields = ['preferred_date','preferred_time_from','preferred_time_to']
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'preferred_time_from': forms.TimeInput(attrs={'type':'time','class':'form-control'}),
            'preferred_time_to': forms.TimeInput(attrs={'type':'time','class':'form-control'}),
        }
