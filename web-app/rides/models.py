from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(blank=True, null=True)
    is_driver = models.BooleanField(default=False)
    def __str__(self):
        return str(user)
    
class Vehicle(models.Model):
    owner = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=255)
    license_plate = models.CharField(max_length=20)
    max_passengers = models.PositiveIntegerField()
    additional_info = models.TextField(blank=True)

class Ride(models.Model):
    owner = models.ForeignKey(UserProfile, related_name='owned_rides', on_delete=models.CASCADE)
    driver = models.ForeignKey(UserProfile, related_name='driven_rides', on_delete=models.CASCADE, null=True, blank=True)
    sharers = models.ManyToManyField(UserProfile, related_name='shared_rides', blank=True)
    starting_location = models.TextField()
    destination_address = models.TextField()
    arrival_datetime = models.DateTimeField()
    total_passengers = models.PositiveIntegerField()
    vehicle_type = models.CharField(max_length=255, blank=True)
    shared_ride = models.BooleanField(default=False)
    additional_info = models.TextField(blank=True)
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('cancelled', 'Cancelled'),
        ('confirmed', 'Confirmed'),
        ('finished', 'Finished'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
