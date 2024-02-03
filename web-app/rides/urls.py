from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.user_login, name="login"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("home/", views.home, name="home"),
    path('profile/', views.profile, name='profile'),
    path('register_driver/', views.register_driver, name='register_driver'),
    path('my_rides', views.my_rides, name='my_rides'),
    path('ride_requset', views.ride_request, name='ride_request'),
]