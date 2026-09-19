from rest_framework import serializers
from appointments.models import Appointment, ServiceType
from users.models import User


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ["id", "name", "duration_minutes", "price", "provider"]
        read_only_fields = ["provider"]


class AppointmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.username", read_only=True)
    provider_name = serializers.CharField(source="provider.username", read_only=True)
    service_name = serializers.CharField(source="service_type.name", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "customer",
            "customer_name",
            "provider",
            "provider_name",
            "service_type",
            "service_name",
            "date",
            "time",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "created_at", "updated_at"]


class AppointmentCreateSerializer(serializers.Serializer):
    provider = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.RoleChoices.PROVIDER)
    )
    date = serializers.DateField()
    time = serializers.TimeField()
    service_type = serializers.PrimaryKeyRelatedField(
        queryset=ServiceType.objects.all(), required=False, allow_null=True
    )

    def validate_time(self, value):
        if value.minute not in [0, 30]:
            raise serializers.ValidationError(
                "Time must be in 30-minute increments (e.g., 10:00 or 10:30)."
            )
        return value
