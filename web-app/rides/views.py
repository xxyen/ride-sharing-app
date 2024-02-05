from django.views.generic import ListView,DetailView
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, LoginForm
from django.contrib.auth import login
from .models import *
from django.db.models import F
from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q

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



# RIDE SEARCH
class RidesIndexView(LoginRequiredMixin, ListView):
    model = Ride
    template_name = 'booking.html'
    context_object_name = 'rides'

    def get_queryset(self):
       
        current_user = self.request.user

        queryset = Ride.objects.filter(
            status='open',
            shared_ride=True,
            driver__isnull=True
        ).exclude(Q(sharers=current_user) | Q(owner=current_user))

        return queryset

# RIDE SEARCH    
def searchRides(response):
    current_user = response.user
    if response.method == 'POST':
        passengers = response.POST.get('passengers')
        destination = response.POST.get('destination_address')
        arrival_time_str = response.POST.get('arrival_datetime')

        print(passengers)
        print(destination)
        print(arrival_time_str)

        arrival_time = datetime.strptime(arrival_time_str, '%Y-%m-%dT%H:%M')
        arrival_time = timezone.make_aware(arrival_time, timezone.get_current_timezone())
        print(arrival_time)
        # total_passengers__lte=F('driver__vehicle__max_passengers') - passengers

        rides = Ride.objects.filter(
            destination_address=destination,
            arrival_datetime=arrival_time,
            shared_ride=True,
            status='open',
            driver__isnull=True,
        ).exclude(Q(sharers=current_user) | Q(owner=current_user))
        # Return a JsonResponse
        
        return render(response, "booking.html", {"rides":rides})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    

# DRIVE SEARCH
class DriveIndexView(LoginRequiredMixin, ListView):
    model = Ride
    template_name = 'driving.html'
    context_object_name = 'rides'

    def get_queryset(self):
       
        current_user = self.request.user

        queryset = Ride.objects.filter(
            status='open',
            driver__isnull=True,
        ).exclude(Q(owner=current_user) | Q(sharers=current_user))

        return queryset
    
# DRIVE SEARCH
def searchDrives(response):
    if response.method == 'POST':
        current_user = response.user
        vehicle_type_input = response.POST.get('vehicle_type')
        additional_info_input = response.POST.get('additional_info')
        capacity = int(response.POST.get('capacity'))

        print(capacity)
        base_query = Q(
            status='open',
            total_passengers__lte=capacity
        )

        # if vehicle_type_input is not none
        if vehicle_type_input:
            base_query &= Q(vehicle_type=vehicle_type_input)

        # if additional_info_input is not none
        if additional_info_input:
            base_query &= Q(additional_info=additional_info_input)

        rides = Ride.objects.filter(base_query).exclude(Q(owner=current_user) | Q(sharers=current_user))

        print(rides)

        # rides = Ride.objects.filter(
        #     Q(vehicle_type__isnull=True) | Q(vehicle_type=vehicle_type_input),
        #     Q(additional_info__isnull=True) | Q(additional_info=additional_info_input),
        #     status='open',
        #     total_passengers__lte=capacity
        # ).exclude(Q(owner=current_user) | Q(sharers=current_user))
        
        return render(response, "driving.html", {"rides": rides})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)





# RIDE CONFIRM
def confirm_passengers(response,pk):
    ride = get_object_or_404(Ride, pk=pk)
    current_passengers = ride.total_passengers
    driver = ride.driver
    # vehicle = driver.vehicle if driver else None
    # max_passengers =  vehicle.max_passengers
    # valid_passengers = max_passengers - current_passengers
    if response.method == "POST":
        passengerCount = response.POST.get('passengerCount')
        if int(passengerCount) > 0 :
            ride.total_passengers = int(passengerCount)
            ride.sharers.add(response.user)
            ride.save() 
            print(ride.total_passengers )
            messages.success(response, "You have successfully joined the ride.")
        else:
            messages.error(response, "You are not a sharer of this ride.")

        return redirect('booking') 
    else:
        return redirect('booking/detail/<int:pk>')

# RIDE DETAIL
class RideDetailView(DetailView):
    model = Ride 
    template_name = "ride-detail.html"
    context_object_name = "ride_content"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Access the related Driver and Vehicle information
        ride = self.get_object()
        # driver = ride.driver
        # vehicle = driver.vehicle if driver else None

        # Add the related data to the context
        # context['ride_content'].vehicle_type = vehicle.vehicle_type
        # context['ride_content'].max_passengers = vehicle.max_passengers
        # context['ride_content'].license_plate = vehicle.license_plate

        arrival_datetime = self.kwargs.get('arrival_datetime')
        passengers = self.kwargs.get('passengers')
        destination_address = self.kwargs.get('destination_address')

        context['ride_content'].custom_date = arrival_datetime
        context['ride_content'].custom_passengers = passengers
        context['ride_content'].custom_destination = destination_address


        return context
    
    
# DRIVE DETAIL   
class DriveDetailView(DetailView):
    model = Ride 
    template_name = "drive-detail.html"
    context_object_name = "ride_content"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Access the related Driver and Vehicle information
        ride = self.get_object()
        # driver = ride.driver
        # vehicle = driver.vehicle if driver else None

        # Add the related data to the context
        # context['ride_content'].vehicle_type = vehicle.vehicle_type
        # context['ride_content'].max_passengers = vehicle.max_passengers
        # context['ride_content'].license_plate = vehicle.license_plate

        arrival_datetime = self.kwargs.get('arrival_datetime')
        passengers = self.kwargs.get('passengers')
        destination_address = self.kwargs.get('destination_address')

        context['ride_content'].custom_date = arrival_datetime
        context['ride_content'].custom_passengers = passengers
        context['ride_content'].custom_destination = destination_address


        return context

# DRIVE CONFIRM
def confirm_driver(response,pk):
    # authentication
    if response.method == "POST":
        print(1111111111111111111)
        if response.user.is_driver:
            print(1111111111111111111)
            ride = get_object_or_404(Ride, pk=pk)
            vehicle = get_object_or_404(Vehicle,owner=response.user)
            max_passengers = vehicle.max_passengers
            current_passengers = ride.total_passengers
            if current_passengers <= max_passengers:
                ride.driver = vehicle.owner
                ride.status = "confirmed"
                ride.save() 
                messages.success(response, "You have successfully confirmed the ride.")
                return redirect('driving')
            else:
                messages.error(response, "Capacity Exceeded.") 
                return redirect('driving/detail/<int:pk>')
        else:
            messages.error(response, "Please verify to become a driver first.")
            return redirect('driving/detail/<int:pk>')
    else:
        return redirect('driving/detail/<int:pk>')
   