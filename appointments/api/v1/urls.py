from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, ServiceTypeViewSet

router = DefaultRouter()
router.register('appointments', AppointmentViewSet, basename='api-appointments')
router.register('service-types', ServiceTypeViewSet, basename='api-service-types')

urlpatterns = [
    path('', include(router.urls)),
]