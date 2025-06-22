from django.db import models
from django.contrib.auth.models import AbstractUser

# -------------------------------
# Custom User Model
# -------------------------------

class User(AbstractUser):
    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)

    def __str__(self):
        return self.username

# -------------------------------
# Patient Profile
# -------------------------------

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    medical_history = models.TextField(blank=True, verbose_name="Medical History")

    def __str__(self):
        return f"{self.user.username} (Patient)"

# -------------------------------
# Doctor Profile
# -------------------------------

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return f"Dr. {self.user.username}"

# -------------------------------
# Appointment Model
# -------------------------------

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Pending Approval', 'Pending Approval')
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    reason = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')

    class Meta:
        unique_together = ('doctor', 'date_time')

    def __str__(self):
        return f"{self.patient.user.username} with {self.doctor.user.username} on {self.date_time}"

# -------------------------------
# Medical Record Model
# -------------------------------

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    prescription = models.TextField()
    lab_results = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("can_add_record", "Can add medical record"),
            ("can_view_record", "Can view medical record"),
        ]


    def __str__(self):
        return f"Record for {self.patient.user.username} by Dr. {self.doctor.user.username} ({self.created_at.date()})"