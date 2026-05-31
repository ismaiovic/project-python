from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('', views.my_appointments, name='my_appointments'),
    path('<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('<int:pk>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('history/', views.medical_history, name='medical_history'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('api/slots/<int:doctor_id>/', views.api_available_slots, name='api_slots'),
]
