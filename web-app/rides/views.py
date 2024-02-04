from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, LoginForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserEditForm, CustomUserPasswordChangeForm, VehicleForm, DriverRegistrationForm, RideRequestForm
from .models import CustomUser, Vehicle, Ride
from django.contrib import messages

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
    
    if request.user.is_driver:
        driven_rides = Ride.objects.filter(driver=request.user)
    else:
        driven_rides = Ride.objects.none()

    rides_categories = [
        ('Owned', owned_rides),
        ('Shared', shared_rides),
        ('Driven', driven_rides),
    ]

    context = {
        'rides_categories': rides_categories,
    }
    return render(request, 'my_rides.html', context)


@login_required
def finish_ride(request, ride_id):
    ride = get_object_or_404(Ride, pk=ride_id)

    if request.method == "POST":
        if request.user == ride.driver and ride.status == 'confirmed':
            ride.status = 'finished'
            ride.save()
            messages.success(request, "The ride has been marked as finished.")
        else:
            messages.error(request, "You are not authorized to finish this ride or the ride is not in the correct state.")

        return redirect('my_rides')  
    else:
        return redirect('my_rides')

@login_required
def quit_ride(request, ride_id):
    ride = get_object_or_404(Ride, pk=ride_id)

    if request.method == "POST":
        if request.user in ride.sharers.all():
            ride.sharers.remove(request.user)
            messages.success(request, "You have successfully quit the ride.")
        else:
            messages.error(request, "You are not a sharer of this ride.")

        return redirect('my_rides') 
    else:
        return redirect('my_rides')

@login_required
def edit_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id, owner=request.user)  # Ensure only the owner can edit
    if request.method == 'POST':
        form = RideRequestForm(request.POST, instance=ride)
        if form.is_valid():
            form.save()
            messages.success(request, "Ride details updated successfully.")
            return redirect('my_rides')
    else:
        form = RideRequestForm(instance=ride)

    return render(request, 'ride_edit.html', {'form': form, 'ride_id': ride.id})  # Render ride_edit.html
