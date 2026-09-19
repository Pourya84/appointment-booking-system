from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.exceptions import ValidationError as DRFValidationError
from datetime import date
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from appointments.models import Appointment, ServiceType
from appointments.services import AppointmentService
from appointments.repositories import AppointmentRepository
from appointments.api.v1.serializers import (
    AppointmentSerializer,
    AppointmentCreateSerializer,
    ServiceTypeSerializer,
)
from appointments.api.v1.permissions import RolePermission
from users.models import User


class AppointmentViewSet(ModelViewSet):
    """
    ViewSet for managing appointments (booking, cancellation, confirmation, rejection).
    """

    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        """
        Override to filter appointments by date.
        By default, only future appointments (today and onwards) are shown.
        Use ?all=true to bypass this filter.
        """
        queryset = super().get_queryset()

        # Only apply filter on list action, unless 'all' param is present
        if self.action == "list" and not self.request.query_params.get("all"):
            queryset = queryset.filter(date__gte=date.today())

        return queryset.order_by("date", "time")

    def get_permissions(self):
        if self.action in ["create", "destroy", "customer_appointments"]:
            self.allowed_roles = ["customer"]
            return [IsAuthenticated(), RolePermission()]
        elif self.action in [
            "confirm",
            "reject",
            "provider_appointments",
            "available_slots",
        ]:
            self.allowed_roles = ["provider"]
            return [IsAuthenticated(), RolePermission()]
        else:
            self.allowed_roles = []
            return [IsAuthenticated()]

    @swagger_auto_schema(
        operation_description="Book a new appointment by the customer.",
        request_body=AppointmentCreateSerializer,
        responses={
            201: AppointmentSerializer(),
            400: "Bad Request - Invalid input data",
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = AppointmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service_type_obj = serializer.validated_data.get("service_type")
        service_type_id = service_type_obj.id if service_type_obj else None

        try:
            appointment = AppointmentService.create_appointment(
                customer=request.user,
                provider=serializer.validated_data["provider"],
                date=serializer.validated_data["date"],
                time_str=serializer.validated_data["time"],
                service_type_id=service_type_id,
            )
            return Response(AppointmentSerializer(appointment).data, status=201)
        except ValidationError as e:
            raise serializers.ValidationError(detail={"error": str(e)})

    @swagger_auto_schema(
        operation_description="Get list of current customer's appointments (requires customer role).",
        responses={200: AppointmentSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="my-appointments")
    def customer_appointments(self, request):
        appointments = AppointmentRepository.get_customer_appointments(request.user)
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get list of current provider's appointments (requires provider role).",
        responses={200: AppointmentSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="provider-appointments")
    def provider_appointments(self, request):
        appointments = AppointmentRepository.get_provider_appointments(request.user)
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Cancel an appointment (by customer or provider).",
        responses={
            200: AppointmentSerializer(),
            403: "You do not have permission to cancel.",
        },
    )
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        try:
            updated = AppointmentService.cancel_appointment(
                appointment.id, request.user
            )
            return Response(AppointmentSerializer(updated).data)
        except ValidationError as e:
            raise DRFValidationError(detail={"error": str(e)})

    @swagger_auto_schema(
        operation_description="Confirm a pending appointment (provider only).",
        responses={
            200: AppointmentSerializer(),
            403: "You do not have permission to confirm.",
        },
    )
    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm(self, request, pk=None):
        appointment = self.get_object()
        try:
            updated = AppointmentService.confirm_appointment(
                appointment.id, request.user
            )
            return Response(AppointmentSerializer(updated).data)
        except ValidationError as e:
            raise DRFValidationError(detail={"error": str(e)})

    @swagger_auto_schema(
        operation_description="Reject a pending appointment (provider only).",
        responses={
            200: AppointmentSerializer(),
            403: "You do not have permission to reject.",
        },
    )
    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        appointment = self.get_object()
        try:
            updated = AppointmentService.reject_appointment(
                appointment.id, request.user
            )
            return Response(AppointmentSerializer(updated).data)
        except ValidationError as e:
            raise DRFValidationError(detail={"error": str(e)})

    @swagger_auto_schema(
        operation_description="Get available time slots for a provider on a specific date.",
        manual_parameters=[
            openapi.Parameter(
                "provider_id",
                openapi.IN_PATH,
                description="Provider ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "date",
                openapi.IN_PATH,
                description="Date in YYYY-MM-DD format",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(
                "List of available slots",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "slots": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                        )
                    },
                ),
            )
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="available-slots/(?P<provider_id>[^/.]+)/(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})",
    )
    def available_slots(self, request, provider_id, date):
        from datetime import datetime

        provider = User.objects.get(id=provider_id, role=User.RoleChoices.PROVIDER)
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        slots = AppointmentRepository.get_available_time_slots(provider, target_date)
        return Response({"slots": slots})


class ServiceTypeViewSet(ReadOnlyModelViewSet):
    """
    ViewSet for listing service types (read-only).
    """

    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get list of all available service types.",
        responses={200: ServiceTypeSerializer(many=True)},
    )
    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get details of a specific service type.",
        responses={200: ServiceTypeSerializer(), 404: "Not found"},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
