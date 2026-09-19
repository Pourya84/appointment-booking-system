from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Schedule(models.Model):
    """
    Defines working hours for a provider on a specific day of the week.
    """

    DAYS_OF_WEEK = [
        (0, "شنبه"),
        (1, "یکشنبه"),
        (2, "دوشنبه"),
        (3, "سه‌شنبه"),
        (4, "چهارشنبه"),
        (5, "پنجشنبه"),
        (6, "جمعه"),
    ]

    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "provider"},
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ("provider", "day_of_week")

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")

    def __str__(self):
        return f"{self.provider.username} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
