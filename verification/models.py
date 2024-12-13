from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from course_registration.models import Registration

class ScanLog(models.Model):
    SCAN_STATUS_CHOICES = [
        ('valid', 'Valid Registration'),
        ('invalid', 'Invalid QR Code'),
        ('expired', 'Expired Registration'),
    ]

    scanned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    scan_timestamp = models.DateTimeField(auto_now_add=True)
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    scan_status = models.CharField(max_length=10, choices=SCAN_STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-scan_timestamp']

    def __str__(self):
        return f"{self.registration.full_name} - {self.scan_timestamp}"