from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    related_appointment_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        if len(self.message) > 29:
            return f"{self.user.username}: {self.message[:30]}..."
        return f"{self.user.username}: {self.message}"
