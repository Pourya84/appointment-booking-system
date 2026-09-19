from datetime import date, datetime, timedelta
from django.db.models import QuerySet
from .models import Appointment, ServiceType, Schedule
from users.models import User


class AppointmentRepository:
    """
    Repository for Appointment model queries.
    Encapsulates all read operations for appointments.
    """

    @staticmethod
    def get_customer_appointments(customer: User, status: str = None) -> QuerySet[Appointment]:
        """
        Get all appointments for a specific customer, optionally filtered by status.
        """
        qs = Appointment.objects.filter(customer=customer).select_related('provider', 'service_type')
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('date', 'time')

    @staticmethod
    def get_provider_appointments(
        provider: User,
        start_date: date = None,
        end_date: date = None
    ) -> QuerySet[Appointment]:
        """
        Get appointments for a specific provider within an optional date range.
        """
        qs = Appointment.objects.filter(provider=provider).select_related('customer', 'service_type')
        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)
        return qs.order_by('date', 'time')

    @staticmethod
    def get_available_time_slots(provider: User, target_date: date) -> list:
        """
        Generate list of available 30-minute time slots for a provider on a given date.
        """
        day_of_week = target_date.weekday()
        schedules = Schedule.objects.filter(provider=provider, day_of_week=day_of_week)
        if not schedules.exists():
            return []

        booked_times = Appointment.objects.filter(
            provider=provider,
            date=target_date
        ).values_list('time', flat=True)

        slots = []
        for schedule in schedules:
            start = schedule.start_time
            end = schedule.end_time
            current = start
            while current < end:
                if current not in booked_times:
                    slots.append(current.strftime("%H:%M"))
                current = (datetime.combine(target_date, current) + timedelta(minutes=30)).time()
        return slots

    @staticmethod
    def get_by_id(appointment_id: int) -> Appointment:
        """
        Retrieve a single appointment by its primary key.
        """
        return Appointment.objects.get(id=appointment_id)

    @staticmethod
    def get_conflicting_appointments(
        provider: User,
        date_obj: date,
        time_obj,
        exclude_id: int = None
    ) -> QuerySet[Appointment]:
        """
        Check if any appointment exists for the same provider, date, and time,
        optionally excluding a specific appointment ID (for updates).
        """
        qs = Appointment.objects.filter(provider=provider, date=date_obj, time=time_obj)
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        return qs


class ServiceTypeRepository:
    """
    Repository for ServiceType model queries.
    """

    @staticmethod
    def get_provider_service_types(provider: User) -> QuerySet[ServiceType]:
        """
        Get all service types offered by a specific provider.
        """
        return ServiceType.objects.filter(provider=provider).order_by('name')

    @staticmethod
    def get_all() -> QuerySet[ServiceType]:
        """
        Get all service types (for admin or general listing).
        """
        return ServiceType.objects.all().order_by('name')

    @staticmethod
    def get_by_id(service_type_id: int) -> ServiceType:
        """
        Retrieve a single service type by its primary key.
        """
        return ServiceType.objects.get(id=service_type_id)