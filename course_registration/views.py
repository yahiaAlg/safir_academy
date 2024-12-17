from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm
from .utils import generate_qr_code, send_registration_email


def home(request):
    return render(request, "course_registration/home.html")


def register(request):
    if request.method == "POST":
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

            return redirect("success", registration_id=registration.registration_id)
    else:

        max_quota = 40  # Example: adjust this as needed
        current_registrations = Registration.objects.distinct("phone").count()
        morning_count = (
            Registration.objects.filter(preferred_schedule="morning")
            .distinct("phone")
            .count()
        )
        afternoon_count = (
            Registration.objects.filter(preferred_schedule="evening")
            .distinct("phone")
            .count()
        )
        print(
            """
              Current registrations: %s
               Morning count: %s
               Afternoon count: %s
            """
            % (current_registrations, morning_count, afternoon_count)
        )

        if current_registrations >= max_quota:
            return render(request, "course_registration/quota_reached.html")
        form = RegistrationForm()

    return render(request, "course_registration/register.html", {"form": form})


def success(request, registration_id):
    return render(
        request,
        "course_registration/success.html",
        {"registration_id": registration_id},
    )


from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Registration


def register_view(request):
    # Check if the registration quota is exceeded

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("success"))  # Redirect to success page
    else:
        form = RegistrationForm()

    return render(request, "course_registration/register.html", {"form": form})
