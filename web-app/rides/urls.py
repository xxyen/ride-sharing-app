from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.user_login, name="login"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("home/", views.home, name="home"),
    path('booking/', views.RidesIndexView.as_view(), name='booking'),
    path('booking/search-rides/',views.searchRides, name = 'search_rides'),
    path('booking/detail/<int:pk>', views.RideDetailView.as_view(),name = 'ride_detail'),
    path('booking/detail/confirm_passenger/<int:pk>',views.confirm_passengers,name = 'confirm_passenger'),
    path('driving/', views.DriveIndexView.as_view(), name='driving'),
    path('driving/search-drives/',views.searchDrives, name = 'search_drives'),
    path('driving/detail/<int:pk>', views.DriveDetailView.as_view(),name = 'drive_detail'),
    path('driving/detail/confirm_driver/<int:pk>',views.confirm_driver,name = 'confirm_driver'),
]