from django.contrib import admin
from .models import ServiceType, Schedule, Appointment


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "provider", "duration_minutes", "price")
    list_filter = ("provider",)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("provider", "day_of_week", "start_time", "end_time")
    list_filter = ("provider", "day_of_week")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("customer", "provider", "date", "time", "status")
    list_filter = ("status", "date", "provider")
    search_fields = ("customer__username", "provider__username")
    raw_id_fields = ("customer", "provider", "service_type")
