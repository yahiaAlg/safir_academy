from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from .models import Registration

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'preferred_schedule', 
                   'registration_date', 'is_email_sent', 'qr_code_preview')
    list_filter = ('preferred_schedule', 'registration_date', 'is_email_sent')
    search_fields = ('full_name', 'email', 'phone', 'registration_id')
    readonly_fields = ('registration_id', 'registration_date', 'qr_code_preview')
    ordering = ('-registration_date',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('registration_id', 'full_name', 'email', 'phone')
        }),
        ('Registration Details', {
            'fields': ('preferred_schedule', 'registration_date', 'is_email_sent')
        }),
        ('QR Code', {
            'fields': ('qr_code', 'qr_code_preview'),
        }),
    )

    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="100" height="100" />', obj.qr_code.url)
        return "No QR Code"
    qr_code_preview.short_description = 'QR Code Preview'

    def has_add_permission(self, request):
        # Registrations should be created through the registration form
        return False