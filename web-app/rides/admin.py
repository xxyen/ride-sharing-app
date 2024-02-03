from django.contrib import admin
from .models import CustomUser, Ride, Vehicle
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Ride)
admin.site.register(Vehicle)