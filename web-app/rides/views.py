from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserEditForm, CustomUserPasswordChangeForm, VehicleForm, DriverRegistrationForm, RideRequestForm
from .models import CustomUser, Vehicle, Ride

# Create your views here.
def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            user = form.save()
            login(response, user)
            return redirect("/home")
    else:
        form = RegisterForm()

    return render(response, "register.html", {"form":form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def home(request):
    return render(request, "home.html")

@login_required
def profile(request):
    try:
        vehicle = request.user.vehicle
    except Vehicle.DoesNotExist:
        vehicle = None

    if request.method == 'POST':
        user_form = CustomUserEditForm(request.POST, instance=request.user)
        vehicle_form = VehicleForm(request.POST, instance=vehicle) if vehicle else None
        password_form = CustomUserPasswordChangeForm(request.user, request.POST)
        if 'edit_user' in request.POST and user_form.is_valid():
            user_form.save()
            return redirect('profile')
        elif 'edit_vehicle' in request.POST and vehicle_form and vehicle_form.is_valid():
            vehicle_form.save()
            return redirect('profile')
        elif 'change_password' in request.POST and password_form.is_valid():
            password_form.save()
            return redirect('profile')
        if 'edit_driver_status' in request.POST:
            driver_status = request.POST.get('driver_status') == 'true'
            request.user.driver_status = driver_status
            request.user.save()
            return redirect('profile')
    else:
        user_form = CustomUserEditForm(instance=request.user)
        vehicle_form = VehicleForm(instance=vehicle) if vehicle else None
        password_form = CustomUserPasswordChangeForm(request.user)

    context = {
        'user_form': user_form,
        'vehicle_form': vehicle_form,
        'password_form': password_form,
        'is_driver': request.user.is_driver,
        'vehicle': vehicle
    }
    return render(request, 'profile.html', context)

@login_required
def register_driver(request):
    if request.method == 'POST':
        form = DriverRegistrationForm(request.POST, owner=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = DriverRegistrationForm()

    return render(request, 'register_driver.html', {'form': form})

@login_required
def ride_request(request):
    if request.method == 'POST':
        form = RideRequestForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.owner = request.user
            ride.save()
            return redirect('my_rides')
    else:
        form = RideRequestForm()
    return render(request, 'ride_request.html', {'form': form})

@login_required
def my_rides(request):
    owned_rides = Ride.objects.filter(owner=request.user)
    shared_rides = Ride.objects.filter(sharers=request.user)
    all_rides = owned_rides | shared_rides 
    context = {'rides': all_rides.distinct()}
    return render(request, 'my_rides.html', context)
