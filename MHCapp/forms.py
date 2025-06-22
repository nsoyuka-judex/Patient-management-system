from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()
from .models import Doctor, Appointment, MedicalRecord

# -------------------------------
# Doctor Registration Forms
# -------------------------------

class DoctorRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        if '<' in username or '>' in username:
            raise forms.ValidationError("Invalid characters in username.")
        return username

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()

    def clean_password(self):
        password = self.cleaned_data['password'].strip()
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        return password

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialization']
        widgets = {
            'specialization': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_specialization(self):
        specialization = self.cleaned_data['specialization'].strip()
        if '<' in specialization or 'script' in specialization.lower():
            raise forms.ValidationError("Specialization must not contain unsafe characters.")
        return specialization


# -------------------------------
# Patient Registration Form
# -------------------------------

class PatientRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()

    def clean_password(self):
        password = self.cleaned_data['password'].strip()
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        return password


# -------------------------------
# Appointment Booking Form
# -------------------------------

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date_time', 'reason']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'date_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

    def clean_reason(self):
        reason = self.cleaned_data['reason'].strip()
        if any(bad in reason.lower() for bad in ['<script>', '</script>', '<iframe>']):
            raise forms.ValidationError("Suspicious characters detected in reason.")
        return reason


# -------------------------------
# Login Form
# -------------------------------

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_username(self):
        return self.cleaned_data['username'].strip()

    def clean_password(self):
        return self.cleaned_data['password'].strip()


# -------------------------------
# Medical Record Form
# -------------------------------

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'prescription', 'lab_results']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prescription': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'lab_results': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_diagnosis(self):
        value = self.cleaned_data['diagnosis'].strip()
        if '<' in value:
            raise forms.ValidationError("Invalid content in diagnosis.")
        return value

    def clean_prescription(self):
        value = self.cleaned_data['prescription'].strip()
        return value

    def clean_lab_results(self):
        value = self.cleaned_data['lab_results'].strip()
        return value