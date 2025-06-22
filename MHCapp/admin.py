from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Patient, Doctor, Appointment, MedicalRecord

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_patient', 'is_doctor', 'is_staff')
    list_filter = ('is_patient', 'is_doctor', 'is_staff')
    search_fields = ('username', 'email')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth')
    search_fields = ('user__username',)

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization')
    search_fields = ('user__username', 'specialization')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date_time', 'status')
    list_filter = ('status', 'date_time')
    search_fields = ('patient__user__username', 'doctor__user__username')

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'created_at')
    search_fields = ('patient__user__username', 'doctor__user__username')
    readonly_fields = ('created_at',)