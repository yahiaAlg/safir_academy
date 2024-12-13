import qrcode
from django.core.mail import EmailMessage
from django.conf import settings
import io
from django.core.files.uploadedfile import InMemoryUploadedFile

def generate_qr_code(registration):
    qr_data = (
        f"Registration ID: {registration.registration_id}\n"
        f"Name: {registration.full_name}\n"
        f"Course: UI/UX Design\n"
        f"Schedule: {registration.get_preferred_schedule_display()}"
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    
    file_name = f"qr_{registration.registration_id}.png"
    file = InMemoryUploadedFile(
        buffer,
        None,
        file_name,
        'image/png',
        buffer.tell(),
        None
    )
    return file

def send_registration_email(registration):
    subject = 'Welcome to Safir Academy UI/UX Course'
    message = f"""
    Dear {registration.full_name},

    Thank you for registering for our UI/UX Design course!

    Registration Details:
    - Registration ID: {registration.registration_id}
    - Schedule: {registration.get_preferred_schedule_display()}
    - Course Start Date: December 19, 2024

    Payment Information:
    - Course Fee: free

    Best regards,
    Safir Academy Team
    """
    
    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [registration.email],
    )
    
    if registration.qr_code:
        email.attach_file(registration.qr_code.path)
    
    return email.send()