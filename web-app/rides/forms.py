from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm,PasswordChangeForm
from django.contrib.auth.models import User
from .models import CustomUser, Vehicle

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=30) 
    last_name = forms.CharField(required=True, max_length=30) 

    class Meta:
        model = CustomUser
        fields = ["username", "email", "first_name", "last_name","password1", "password2"]

class LoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')

class CustomUserEditForm(UserChangeForm):
    password = None 

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email']

class CustomUserPasswordChangeForm(PasswordChangeForm):
    pass

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['vehicle_type', 'license_plate', 'max_passengers', 'additional_info']

class DriverRegistrationForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['vehicle_type', 'license_plate', 'max_passengers', 'additional_info']

    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        vehicle = super().save(commit=False)
        vehicle.owner = self.owner
        if commit:
            vehicle.owner.is_driver = True
            vehicle.owner.driver_status = True
            vehicle.owner.save()
            vehicle.save()
        return vehicle