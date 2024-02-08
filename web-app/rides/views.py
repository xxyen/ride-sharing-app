
from .forms import RegisterForm, LoginForm
from django.contrib.auth import login
from django.views.generic import ListView,DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CustomUserEditForm, CustomUserPasswordChangeForm, VehicleForm, DriverRegistrationForm, RideRequestForm
from .models import Vehicle, Ride
from django.contrib import messages

from .models import *
from datetime import datetime
from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
import os.path
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import requests
# Authentication and service creation
def gmail_authenticate():
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None
    # token.json stored user access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Authentication if no valid credentials are available
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This credentials.json is the credential you download from Google API portal when you 
            # created the OAuth 2.0 Client IDs
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            # this is the redirect URI which should match your API setting, you can 
            # find this setting in Credentials/Authorized redirect URIs at the API setting portal
            creds = flow.run_local_server(host='vcm-38514.vm.duke.edu', port=8080)
        # Save vouchers for later use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

# Create and send emails
def send_message(service, sender, to, subject, msg_html):
    message = MIMEMultipart('alternative')
    message['from'] = sender
    message['to'] = to
    message['subject'] = subject

    msg = MIMEText(msg_html, 'html')
    message.attach(msg)

    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}

    message = (service.users().messages().send(userId="me", body=body).execute())
    print(f"Message Id: {message['id']}")




# SEND EMAIL TO USER
def sendEmailAuto(request,pk):
    if request.method == 'POST':
        ride = get_object_or_404(Ride,pk=pk)
        all_users = list(ride.sharers.all()) + [ride.owner]
        user = all_users[0]
        driver_name = request.user.username
        service = gmail_authenticate()
        for user in all_users:
            print(user.email)
            send_message(service, "xueqianyi222@gmail.com", user.email, "Your Ride Confirmation", f'Dear {user.last_name},\n\n Your ride has been confirmed by the driver {driver_name}. Thank you for using our service.')
            print(1111)



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
        
        return render(response, "driving.html", {"rides": rides})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)





# RIDE CONFIRM
def confirm_passengers(response,pk):
    ride = get_object_or_404(Ride, pk=pk)
    current_passengers = ride.total_passengers
    driver = ride.driver
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
def confirm_driver(request,pk):
    # authentication
    if request.method == "POST":
        if request.user.is_driver:
            if request.user.driver_status:
                ride = get_object_or_404(Ride, pk=pk)
                vehicle = get_object_or_404(Vehicle,owner=request.user)
                max_passengers = vehicle.max_passengers
                current_passengers = ride.total_passengers
                if current_passengers <= max_passengers:
                    ride.driver = vehicle.owner
                    ride.status = "confirmed"
                    ride.save() 
                    sendEmailAuto(request,pk)
                    # messages.success(request, "You have successfully confirmed the ride.")
                    # return redirect('driving')      
                    return JsonResponse({
                    'title': 'Success',
                    'message': 'You have successfully confirmed the ride.',
                    'redirect': '/my_rides'
                })          
                else:
                    # print(333333333333333333)
                    # messages.error(request, "Capacity Exceeded.") 
                    # return redirect('driving')
                     # 返回容量超出的JSON响应
                    return JsonResponse({
                        'title': 'Error',
                        'message': 'Capacity exceeded. You cannot take this ride.',
                        'redirect': '/driving' 
                    })
            else:
                # print(222222222222222)
                # messages.error(request, "Please set your driver status to OPEN.")
                # print(222222222222222)
                # return redirect('profile')
                return JsonResponse({
                'title': 'Error',
                'message': 'Please set your driver status to OPEN.',
                'redirect': '/profile' 
            })
        else:
            # print(11111111111111111)
            # messages.error(request, "Please verify to become a driver first.")
            # return redirect('profile')
            return JsonResponse({
            'title': 'Error',
            'message': 'You are not authorized to confirm rides as a driver.',
            'redirect': '/profile' 
        })
        

    return redirect('profile')