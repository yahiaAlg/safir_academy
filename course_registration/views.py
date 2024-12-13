from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm
from .utils import generate_qr_code, send_registration_email

def home(request):
    return render(request, 'course_registration/home.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            
            # Generate and save QR code
            qr_code = generate_qr_code(registration)
            registration.qr_code.save(f"qr_{registration.registration_id}.png", qr_code)
            
            registration.save()
            
            # Send email
            if send_registration_email(registration):
                registration.is_email_sent = True
                registration.save()
            
            return redirect('success', registration_id=registration.registration_id)
    else:
        form = RegistrationForm()
    
    return render(request, 'course_registration/register.html', {'form': form})

def success(request, registration_id):
    return render(request, 'course_registration/success.html', {'registration_id': registration_id})