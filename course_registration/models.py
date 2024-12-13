from django.db import models
import uuid

class Registration(models.Model):
    SCHEDULE_CHOICES = [
        ('morning', 'Morning Session (8 AM - 12 AM)'),
        ('evening', 'Evening Session (1 PM - 4 PM)'),
    ]
    
    registration_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    preferred_schedule = models.CharField(max_length=10, choices=SCHEDULE_CHOICES)
    registration_date = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    is_email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {self.registration_id}"