from django.urls import path
from . import views_html

urlpatterns = [
    # Customer
    path('app/customer/dashboard/', views_html.customer_dashboard, name='customer_dashboard'),
    path('app/customer/create/', views_html.create_appointment_step1, name='create_appointment_step1'),
    path('app/customer/create/step2/', views_html.create_appointment_step2, name='create_appointment_step2'),

    # Provider
    path('app/provider/dashboard/', views_html.provider_dashboard, name='provider_dashboard'),
    path('app/provider/calendar/', views_html.provider_calendar, name='provider_calendar'),
    path('app/provider/schedules/', views_html.manage_schedules, name='manage_schedules'),
    path('app/provider/schedules/add/', views_html.add_schedule, name='add_schedule'),
    path('app/provider/schedules/<int:schedule_id>/delete/', views_html.delete_schedule, name='delete_schedule'),
    path('app/provider/service-types/', views_html.manage_service_types, name='manage_service_types'),
    path('app/provider/service-types/add/', views_html.add_service_type, name='add_service_type'),
    path('app/provider/service-types/<int:service_type_id>/edit/', views_html.edit_service_type, name='edit_service_type'),
    path('app/provider/service-types/<int:service_type_id>/delete/', views_html.delete_service_type, name='delete_service_type'),

    # Common (cancel)
    path('app/appointment/<int:appointment_id>/cancel/', views_html.cancel_appointment, name='cancel_appointment'),
    path('app/provider/confirm/<int:appointment_id>/', views_html.confirm_appointment, name='confirm_appointment'),
    path('app/provider/reject/<int:appointment_id>/', views_html.reject_appointment, name='reject_appointment'),
]