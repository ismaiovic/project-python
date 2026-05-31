from django.urls import path
from . import views

urlpatterns = [
    path('', views.doctor_list, name='doctor_list'),
    path('<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('<int:pk>/review/', views.submit_review, name='submit_review'),
    path('my-profile/', views.my_profile, name='doctor_my_profile'),
    path('availability/', views.manage_availability, name='manage_availability'),
    path('availability/<int:pk>/delete/', views.delete_availability, name='delete_availability'),
]
