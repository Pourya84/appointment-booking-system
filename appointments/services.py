from django.core.exceptions import ValidationError
from django.db import transaction
from datetime import datetime
from .models import Appointment, ServiceType, Schedule
from .repositories import AppointmentRepository


class AppointmentService:
    """
    Service layer for appointment business logic.
    All methods are static to avoid instantiation.
    """

    @staticmethod
    @transaction.atomic
    def create_appointment(customer, provider, date, time_str, service_type_id):
        """
        Create a new appointment after validating working hours,
        conflict, and service type existence.
        """
        date_obj = AppointmentService._parse_date(date)
        time_obj = AppointmentService._parse_time(time_str)

        AppointmentService._validate_working_hours(provider, date_obj, time_obj)
        AppointmentService._check_no_conflict(provider, date_obj, time_obj)
        service_type = AppointmentService._get_service_type(provider, service_type_id)

        return AppointmentService._create_appointment_record(
            customer, provider, date_obj, time_obj, service_type
        )

    # ---------- Private helper methods ----------

    @staticmethod
    def _parse_date(date_input):
        """Convert string date to date object if needed."""
        if isinstance(date_input, str):
            return datetime.strptime(date_input, "%Y-%m-%d").date()
        return date_input

    @staticmethod
    def _parse_time(time_input):
        """Convert string time to time object if needed."""
        if isinstance(time_input, str):
            return datetime.strptime(time_input, "%H:%M").time()
        return time_input

    @staticmethod
    def _validate_working_hours(provider, date_obj, time_obj):
        """
        Ensure the requested time falls within the provider's working hours
        for that day of the week.
        """
        day_of_week = date_obj.weekday()
        if not Schedule.objects.filter(
            provider=provider,
            day_of_week=day_of_week,
            start_time__lte=time_obj,
            end_time__gte=time_obj,
        ).exists():
            raise ValidationError(
                "The selected time is not within the provider's working hours."
            )

    @staticmethod
    def _check_no_conflict(provider, date_obj, time_obj):
        """
        Ensure no other appointment exists for the same provider, date, and time.
        """
        if AppointmentRepository.get_conflicting_appointments(
            provider, date_obj, time_obj
        ).exists():
            raise ValidationError(
                "This time slot has already been booked by someone else."
            )

    @staticmethod
    def _get_service_type(provider, service_type_id):
        """
        Retrieve the service type instance if ID is provided.
        """
        if not service_type_id:
            return None

        if isinstance(service_type_id, ServiceType):
            return service_type_id

        return ServiceType.objects.get(id=service_type_id, provider=provider)

    @staticmethod
    def _create_appointment_record(
        customer, provider, date_obj, time_obj, service_type
    ):
        """
        Create and return the Appointment instance with status 'pending'.
        """
        return Appointment.objects.create(
            customer=customer,
            provider=provider,
            date=date_obj,
            time=time_obj,
            service_type=service_type,
            status="pending",
        )

    # ---------- Public action methods ----------

    @staticmethod
    def cancel_appointment(appointment_id, user):
        """
        Cancel an appointment if the user is the customer or provider.
        """
        from notifications.models import Notification

        appointment = Appointment.objects.get(id=appointment_id)

        if user != appointment.customer and user != appointment.provider:
            raise ValidationError("You are not allowed to cancel this appointment.")

        if appointment.status not in ["pending", "confirmed"]:
            raise ValidationError("This appointment cannot be cancelled.")

        appointment.status = "cancelled"
        appointment.save()

        Notification.objects.create(
            user=appointment.customer,
            message=f"Your appointment on {appointment.date} at {appointment.time} has been cancelled.",
            related_appointment_id=appointment.id,
        )

        if user == appointment.customer:
            Notification.objects.create(
                user=appointment.provider,
                message=(
                    f"Appointment for {appointment.customer.username} "
                    f"on {appointment.date} at {appointment.time} was cancelled by the customer."
                ),
                related_appointment_id=appointment.id,
            )

        return appointment

    @staticmethod
    def confirm_appointment(appointment_id, provider):
        """
        Confirm a pending appointment by the provider.
        """
        from notifications.models import Notification

        appointment = Appointment.objects.get(id=appointment_id)

        if appointment.provider != provider:
            raise ValidationError("Only the provider can confirm this appointment.")

        if appointment.status != "pending":
            raise ValidationError("Only pending appointments can be confirmed.")

        appointment.status = "confirmed"
        appointment.save()

        Notification.objects.create(
            user=appointment.customer,
            message=(
                f"Your appointment on {appointment.date} at {appointment.time} "
                f"has been confirmed by {provider.username}."
            ),
            related_appointment_id=appointment.id,
        )

        return appointment

    @staticmethod
    def reject_appointment(appointment_id, provider):
        """
        Reject a pending appointment by the provider.
        """
        from notifications.models import Notification

        appointment = Appointment.objects.get(id=appointment_id)

        if appointment.provider != provider:
            raise ValidationError("Only the provider can reject this appointment.")

        if appointment.status != "pending":
            raise ValidationError("Only pending appointments can be rejected.")

        appointment.status = "rejected"
        appointment.save()

        Notification.objects.create(
            user=appointment.customer,
            message=(
                f"Your appointment on {appointment.date} at {appointment.time} "
                f"has been rejected by {provider.username}."
            ),
            related_appointment_id=appointment.id,
        )

        return appointment
