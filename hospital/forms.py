from django import forms
from django.contrib.auth.models import User
from . import models
from django.contrib.auth.forms import UserCreationForm   # 👈 thêm dòng này




#for admin signup
class AdminSigupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2']


#for student related form
class DoctorUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }
class DoctorForm(forms.ModelForm):
    class Meta:
        model = models.Doctor
        fields = ['address', 'mobile', 'department', 'profile_pic']




#for teacher related form
class PatientUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }
class PatientForm(forms.ModelForm):
    #this is the extrafield for linking patient and their assigend doctor
    #this will show dropdown __str__ method doctor model is shown on html so override it
    #to_field_name this will fetch corresponding value  user_id present in Doctor model and return it
    assignedDoctorId=forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True),empty_label="Name and Department", to_field_name="user_id")
    class Meta:
        model=models.Patient
        fields=['address','mobile','status','symptoms','profile_pic']



class AppointmentForm(forms.ModelForm):
    doctorId = forms.ModelChoiceField(
        queryset=models.Doctor.objects.all().filter(status=True),
        empty_label="Doctor Name and Department", 
        to_field_name="user_id"
    )
    patientId = forms.ModelChoiceField(
        queryset=models.Patient.objects.all().filter(status=True),
        empty_label="Patient Name and Symptoms", 
        to_field_name="user_id"
    )
    appointment_datetime = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M'],  # Thêm dòng này để Django hiểu dữ liệu từ datetime-local
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })
    )

    class Meta:
        model = models.Appointment
        fields = ['description', 'status', 'appointment_datetime']



class PatientAppointmentForm(forms.ModelForm):
    doctorId = forms.ModelChoiceField(
        queryset=models.Doctor.objects.all().filter(status=True),
        empty_label="Doctor Name and Department", 
        to_field_name="user_id"
    )
    appointment_datetime = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M'],  # Thêm dòng này để hỗ trợ định dạng HTML5 datetime-local
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })
    )

    class Meta:
        model = models.Appointment
        fields = ['description', 'status', 'appointment_datetime']



#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))




