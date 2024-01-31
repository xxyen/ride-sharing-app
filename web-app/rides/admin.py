from django.contrib import admin
from .models import UserProfile, Ride, Vehicle
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Ride)
admin.site.register(Vehicle)