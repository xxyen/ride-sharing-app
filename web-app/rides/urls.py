from django.contrib import admin
from django.urls import path
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
    path('quit-ride/<int:ride_id>/', views.quit_ride, name='quit_ride'),
    path('finish-ride/<int:ride_id>/', views.finish_ride, name='finish_ride'),
    path('edit_ride/<int:ride_id>/', views.edit_ride, name='edit_ride'),

    path('booking/', views.RidesIndexView.as_view(), name='booking'),
    path('booking/search-rides/',views.searchRides, name = 'search_rides'),
    path('booking/detail/<int:pk>', views.RideDetailView.as_view(),name = 'ride_detail'),
    path('booking/detail/confirm_passenger/<int:pk>',views.confirm_passengers,name = 'confirm_passenger'),
    path('driving/', views.DriveIndexView.as_view(), name='driving'),
    path('driving/search-drives/',views.searchDrives, name = 'search_drives'),
    path('driving/detail/<int:pk>', views.DriveDetailView.as_view(),name = 'drive_detail'),
    path('driving/detail/confirm_driver/<int:pk>',views.confirm_driver,name = 'confirm_driver'),
]