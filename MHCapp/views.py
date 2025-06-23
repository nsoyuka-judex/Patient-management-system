from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django_ratelimit.decorators import ratelimit


from .models import User, Patient, Doctor, Appointment, MedicalRecord
from .forms import (
    LoginForm,
    PatientRegisterForm,
    DoctorRegisterForm,
    DoctorProfileForm,
    AppointmentForm,
    MedicalRecordForm
)

# -----------------------------
# Home View
# -----------------------------
def home(request):
    return render(request, 'MHCapp/home.html')


# -----------------------------
# Authentication Views
# -----------------------------
@ratelimit(key='ip', rate='5/m', block=True)
def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_doctor:
                return redirect('doctor_dashboard')
            elif user.is_patient:
                return redirect('patient_dashboard')
            return redirect('home')
        else:
            messages.error(request, "Invalid login credentials.")
    return render(request, 'MHCapp/login.html', {"form": form})


def logout_view(request):
    logout(request)
    return redirect('home')


# -----------------------------
# Patient Registration
# -----------------------------
@ratelimit(key='ip', rate='3/m', block=True)
def register_patient(request):
    form = PatientRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.is_patient = True
        user.save()
        Patient.objects.create(user=user)
        login(request, user)
        return redirect('patient_dashboard')
    return render(request, 'MHCapp/register.html', {"form": form})


# -----------------------------
# Doctor Registration
# -----------------------------
@ratelimit(key='ip', rate='3/m', block=True)
def register_doctor(request):
    user_form = DoctorRegisterForm(request.POST or None)
    profile_form = DoctorProfileForm(request.POST or None)
    if user_form.is_valid() and profile_form.is_valid():
        user = user_form.save(commit=False)
        user.set_password(user_form.cleaned_data['password'])
        user.is_doctor = True
        user.save()
        doctor = profile_form.save(commit=False)
        doctor.user = user
        doctor.save()
        login(request, user)
        return redirect('doctor_dashboard')
    return render(request, 'MHCapp/register_doctor.html', {
        "user_form": user_form,
        "profile_form": profile_form
    })


# -----------------------------
# Dashboards
# -----------------------------
@login_required
def patient_dashboard(request):
    if not request.user.is_patient:
        return redirect('home')
    patient = get_object_or_404(Patient, user=request.user)
    appointments = Appointment.objects.filter(patient=patient).order_by('-date_time')
    return render(request, 'MHCapp/patient_dashboard.html', {'appointments': appointments})


@login_required
def doctor_dashboard(request):
    if not request.user.is_doctor:
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-date_time')

    return render(request, 'MHCapp/doctor_dashboard.html', {
        'appointments': appointments,
        'doctor': doctor,
    })
# -----------------------------
# Book Appointment
# -----------------------------
@ratelimit(key='user_or_ip', rate='10/m', block=True)
@login_required
def book_appointment(request):
    if not request.user.is_patient:
        return redirect('home')
    form = AppointmentForm(request.POST or None)
    if form.is_valid():
        appointment = form.save(commit=False)
        appointment.patient = request.user.patient
        appointment.status = 'Scheduled'
        appointment.save()
        messages.success(request, "Appointment booked.")
        return redirect('patient_dashboard')
    return render(request, 'MHCapp/book_appointment.html', {'form': form})



# -----------------------------
# Appointment Status Actions
# -----------------------------
@login_required
def approve_appointment(request, appointment_id):
    if not request.user.is_doctor:
        return redirect('home')
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    appointment.status = 'Scheduled'
    appointment.save()
    messages.success(request, "Appointment approved.")
    return redirect('doctor_dashboard')


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    if request.user == appointment.doctor.user or request.user == appointment.patient.user:
        appointment.status = 'Cancelled'
        appointment.save()
        messages.warning(request, "Appointment cancelled.")
    return redirect('doctor_dashboard' if request.user.is_doctor else 'patient_dashboard')


@login_required
def complete_appointment(request, appointment_id):
    if not request.user.is_doctor:
        return redirect('home')
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    appointment.status = 'Completed'
    appointment.save()
    messages.success(request, "Appointment marked as completed.")
    return redirect('doctor_dashboard')


# -----------------------------
# Medical Records
# -----------------------------
@login_required
@permission_required('MHCapp.can_add_record', raise_exception=True)
def add_medical_record(request, patient_id):
    doctor = get_object_or_404(Doctor, user=request.user)
    patient = get_object_or_404(Patient, pk=patient_id)

    form = MedicalRecordForm(request.POST or None)
    if form.is_valid():
        record = form.save(commit=False)
        record.patient = patient
        record.doctor = doctor
        record.save()
        messages.success(request, "Medical record added successfully.")
        return redirect('view_patient_records', patient_id=patient.id)

    return render(request, 'MHCapp/add_record.html', {
        'form': form,
        'patient': patient
    })

@ratelimit(key='user_or_ip', rate='15/m', block=True)
@login_required
def view_patient_records(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    # Allow the patient to see their own records
    if hasattr(request.user, 'patient') and request.user.patient.id != patient.id:
        raise PermissionDenied

    # Allow a doctor to see all patient records
    if not hasattr(request.user, 'patient') and not hasattr(request.user, 'doctor'):
        raise PermissionDenied

    records = MedicalRecord.objects.filter(patient=patient).select_related('doctor')
    return render(request, 'MHCapp/view_patient_records.html', {
        'patient': patient,
        'records': records
    })


@login_required
def patient_medical_records(request):
    if not request.user.is_patient:
        return redirect('home')
    patient = get_object_or_404(Patient, user=request.user)
    records = MedicalRecord.objects.filter(patient=patient)
    return render(request, 'MHCapp/my_records.html', {'records': records})
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def doctor_appointments(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-date_time')
    return render(request, 'MHCapp/doctor_appointments.html', {'appointments': appointments})

@ratelimit(key='user_or_ip', rate='15/m', block=True)
@login_required
def search_patient(request):
    query = request.GET.get('q')
    patients = Patient.objects.filter(user__username__icontains=query) if query else []
    return render(request, 'MHCapp/search_patient.html', {'patients': patients, 'query': query})
@ratelimit(key='user_or_ip', rate='10/m', block=True)
@login_required
def doctor_messages(request):
    return render(request, 'MHCapp/doctor_messages.html')


@ratelimit(key='user_or_ip', rate='10/m', block=True)
@login_required
def add_medical_record(request, patient_id):
    # Ensure the user is a doctor
    if not hasattr(request.user, 'doctor'):
        return HttpResponseForbidden("Only doctors are allowed to add medical records.")

    doctor = get_object_or_404(Doctor, user=request.user)
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = patient
            record.doctor = doctor
            record.save()
            messages.success(request, "Medical record added successfully.")
            return redirect('view_patient_records', patient_id=patient.id)
    else:
        form = MedicalRecordForm()

    return render(request, 'MHCapp/add_medical_record.html', {
        'form': form,
        'patient': patient
    })
@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient__user=request.user)

    if appointment.status not in ['Cancelled', 'Approved']:  # Prevent cancelling an already cancelled or completed one
        appointment.status = 'Cancelled'
        appointment.save()
        messages.success(request, "Appointment successfully cancelled.")

    return redirect('patient_dashboard')

