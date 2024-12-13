from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from .models import ScanLog

@admin.register(ScanLog)
class ScanLogAdmin(admin.ModelAdmin):
    list_display = ('get_registrant_name', 'scanned_by', 'scan_timestamp', 
                   'scan_status', 'get_preferred_schedule')
    list_filter = ('scan_status', 'scan_timestamp', 'scanned_by')
    search_fields = ('registration__full_name', 'registration__email', 
                    'scanned_by__username', 'notes')
    readonly_fields = ('scan_timestamp',)
    ordering = ('-scan_timestamp',)
    
    fieldsets = (
        ('Scan Information', {
            'fields': ('scan_timestamp', 'scan_status', 'scanned_by')
        }),
        ('Registration Details', {
            'fields': ('registration',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

    def get_registrant_name(self, obj):
        return obj.registration.full_name
    get_registrant_name.short_description = 'Registrant Name'
    get_registrant_name.admin_order_field = 'registration__full_name'

    def get_preferred_schedule(self, obj):
        return obj.registration.get_preferred_schedule_display()
    get_preferred_schedule.short_description = 'Preferred Schedule'
    get_preferred_schedule.admin_order_field = 'registration__preferred_schedule'

    def has_add_permission(self, request):
        # Scan logs should only be created through the scanning process
        return False

    def has_change_permission(self, request, obj=None):
        # Only allow editing notes
        return True

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('registration', 'scanned_by', 'scan_status')
        return self.readonly_fields