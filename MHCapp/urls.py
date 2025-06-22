from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Registration
    path('register/', views.register_patient, name='register'),
    path('register/doctor/', views.register_doctor, name='register_doctor'),

    # Dashboards
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/doctor/', views.doctor_dashboard, name='doctor_dashboard'),

    # Appointment booking
    path('book/', views.book_appointment, name='book_appointment'),

    # Appointment actions (Doctor)
    path('appointment/<int:appointment_id>/approve/', views.approve_appointment, name='approve_appointment'),
    path('appointment/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointment/<int:appointment_id>/complete/', views.complete_appointment, name='complete_appointment'),

    # Medical Records
    path('patient/<int:patient_id>/records/', views.view_patient_records, name='view_patient_records'),  # Doctor view
    path('my-records/', views.patient_medical_records, name='patient_medical_records'),  # Patient view
    path('patient/<int:patient_id>/add-record/', views.add_medical_record, name='add_medical_record'),
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/search/', views.search_patient, name='search_patient'),
    path('doctor/messages/', views.doctor_messages, name='doctor_messages')
]