from django.db.models.signals import post_save
from django.dispatch import receiver
from appointments.models import Appointment
from .models import Notification


@receiver(post_save, sender=Appointment)
def appointment_notification(sender, instance, created, **kwargs):
    """
    Send notifications to customer and provider when a new appointment is created.
    """
    if created:
        # Notify the customer
        Notification.objects.create(
            user=instance.customer,
            message=(
                f"Your appointment on {instance.date} at {instance.time} "
                f"with {instance.provider.username} has been successfully booked."
            ),
            related_appointment_id=instance.id,
        )

        # Notify the provider
        Notification.objects.create(
            user=instance.provider,
            message=(
                f"New appointment request from {instance.customer.username} "
                f"for {instance.date} at {instance.time} has been registered."
            ),
            related_appointment_id=instance.id,
        )
