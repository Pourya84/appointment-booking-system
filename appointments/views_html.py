import calendar
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from users.decorators import require_role
from users.models import User

from .models import Schedule, ServiceType, Appointment
from .repositories import AppointmentRepository
from .services import AppointmentService

# ==================================================
# Home page
# ==================================================

def home_view(request):
    """
    Home page - redirects based on user role.
    """
    if request.user.is_authenticated:
        if request.user.role == User.RoleChoices.CUSTOMER:
            return redirect("customer_dashboard")
        elif request.user.role == User.RoleChoices.PROVIDER:
            return redirect("provider_dashboard")
        elif request.user.role == User.RoleChoices.ADMIN:
            return redirect("/admin/")
        return redirect("login")
    return redirect("login")


# ==================================================
# Customer Section
# ==================================================

@login_required
@require_role([User.RoleChoices.CUSTOMER])
def customer_dashboard(request):
    """Customer dashboard – list of their appointments with cancel option."""
    appointments = AppointmentRepository.get_customer_appointments(request.user)
    return render(
        request,
        "appointments/customer_dashboard.html",
        {"appointments": appointments},
    )


@login_required
@require_role([User.RoleChoices.CUSTOMER])
def create_appointment_step1(request):
    """Step 1 of booking: select provider and date – show available time slots."""
    providers = User.objects.filter(role=User.RoleChoices.PROVIDER)
    selected_provider_id = request.GET.get("provider")
    selected_date = request.GET.get("date")
    available_slots = []
    service_types = []

    if selected_provider_id and selected_date:
        provider = get_object_or_404(User, id=selected_provider_id, role=User.RoleChoices.PROVIDER)
        try:
            target_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
            if target_date < date.today():
                messages.error(request, "تاریخ انتخابی نمی‌تواند در گذشته باشد")
            else:
                available_slots = AppointmentRepository.get_available_time_slots(
                    provider, target_date
                )
                service_types = ServiceType.objects.filter(provider=provider)
        except ValueError:
            messages.error(request, "تاریخ نامعتبر است")

    context = {
        "providers": providers,
        "selected_provider_id": selected_provider_id,
        "selected_date": selected_date,
        "available_slots": available_slots,
        "service_types": service_types,
    }
    return render(request, "appointments/create_appointment.html", context)


@login_required
@require_role([User.RoleChoices.CUSTOMER])
def create_appointment_step2(request):
    """Step 2 of booking: get form data and create appointment."""
    if request.method == "POST":
        provider_id = request.POST.get("provider")
        date_str = request.POST.get("date")
        time_str = request.POST.get("time")
        service_type_id = request.POST.get("service_type")

        try:
            provider = get_object_or_404(User, id=provider_id, role=User.RoleChoices.PROVIDER)
            AppointmentService.create_appointment(
                customer=request.user,
                provider=provider,
                date=date_str,
                time_str=time_str,
                service_type_id=service_type_id,
            )
            messages.success(request, "نوبت با موفقیت رزرو شد.")
        except Exception as e:
            messages.error(request, str(e))
        return redirect("customer_dashboard")

    return redirect("create_appointment_step1")


# ==================================================
# General Section (cancel appointment)
# ==================================================

@login_required
def cancel_appointment(request, appointment_id):
    """Cancel appointment by customer or provider (based on user role)."""
    if request.method == "POST":
        try:
            AppointmentService.cancel_appointment(appointment_id, request.user)
            messages.success(request, "نوبت لغو شد.")
        except Exception as e:
            messages.error(request, str(e))

    if request.user.role == User.RoleChoices.CUSTOMER:
        return redirect("customer_dashboard")
    elif request.user.role == User.RoleChoices.PROVIDER:
        return redirect("provider_dashboard")
    return redirect("home")


# ==================================================
# Provider Section
# ==================================================

@login_required
@require_role([User.RoleChoices.PROVIDER])
def provider_dashboard(request):
    today_date = date.today()
    appointments = AppointmentRepository.get_provider_appointments(
        request.user, start_date=today_date
    )
    return render(
        request,
        "appointments/provider_dashboard.html",
        {"appointments": appointments},
    )


@login_required
@require_role([User.RoleChoices.PROVIDER])
def confirm_appointment(request, appointment_id):
    """Confirm appointment by provider."""
    if request.method == "POST":
        try:
            AppointmentService.confirm_appointment(appointment_id, request.user)
            messages.success(request, "نوبت تایید شد.")
        except Exception as e:
            messages.error(request, str(e))
    return redirect("provider_dashboard")


@login_required
@require_role([User.RoleChoices.PROVIDER])
def reject_appointment(request, appointment_id):
    """Reject appointment by provider."""
    if request.method == "POST":
        try:
            AppointmentService.reject_appointment(appointment_id, request.user)
            messages.success(request, "نوبت رد شد.")
        except Exception as e:
            messages.error(request, str(e))
    return redirect("provider_dashboard")


# ==================================================
# Advanced Calendar (day/week/month) for provider
# ==================================================

@login_required
@require_role([User.RoleChoices.PROVIDER])
def provider_calendar(request):
    """
    Display provider's appointments in calendar format.
    Supports day, week, month views (GET parameter: view).
    """
    view_type = request.GET.get("view", "day")  # day, week, month
    today = datetime.today().date()

    # Determine date range based on view type
    if view_type == "day":
        start_date = today
        end_date = today
    elif view_type == "week":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif view_type == "month":
        start_date = today.replace(day=1)
        last_day = calendar.monthrange(today.year, today.month)[1]
        end_date = today.replace(day=last_day)
    else:
        start_date = today
        end_date = today

    # Get appointments from repository
    appointments = AppointmentRepository.get_provider_appointments(
        request.user, start_date, end_date
    )

    # Build a sorted list of (date, list of appointments) for all days in the range
    date_appointments = []
    current_date = start_date
    while current_date <= end_date:
        day_apps = [apt for apt in appointments if apt.date == current_date]
        date_appointments.append((current_date, day_apps))
        current_date += timedelta(days=1)

    context = {
        "date_appointments": date_appointments,
        "view_type": view_type,
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "appointments/provider_calendar.html", context)


# ==================================================
# Working Hours Management (CRUD Schedule) by provider
# ==================================================

@login_required
@require_role([User.RoleChoices.PROVIDER])
def manage_schedules(request):
    """List provider's working hours for management."""
    schedules = Schedule.objects.filter(provider=request.user).order_by(
        "day_of_week", "start_time"
    )
    return render(
        request,
        "appointments/manage_schedules.html",
        {"schedules": schedules},
    )


@login_required
@require_role([User.RoleChoices.PROVIDER])
def add_schedule(request):
    """Form to add new working hours."""
    if request.method == "POST":
        day_of_week = request.POST.get("day_of_week")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        try:
            Schedule.objects.create(
                provider=request.user,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
            )
            messages.success(request, "ساعت کاری با موفقیت اضافه شد.")
        except Exception as e:
            messages.error(request, str(e))
        return redirect("manage_schedules")

    return render(request, "appointments/add_schedule.html")


@login_required
@require_role([User.RoleChoices.PROVIDER])
def delete_schedule(request, schedule_id):
    """Delete working hours (only if owned by the provider)."""
    schedule = get_object_or_404(Schedule, id=schedule_id, provider=request.user)
    if request.method == "POST":
        schedule.delete()
        messages.success(request, "ساعت کاری حذف شد.")
    return redirect("manage_schedules")


# ==================================================
# Service Types Management by provider
# ==================================================

@login_required
@require_role([User.RoleChoices.PROVIDER])
def manage_service_types(request):
    """List current provider's service types."""
    service_types = ServiceType.objects.filter(provider=request.user).order_by("name")
    return render(
        request,
        "appointments/manage_service_types.html",
        {"service_types": service_types},
    )


@login_required
@require_role([User.RoleChoices.PROVIDER])
def add_service_type(request):
    """Add a new service."""
    if request.method == "POST":
        name = request.POST.get("name")
        duration_minutes = request.POST.get("duration_minutes")
        price = request.POST.get("price")
        try:
            ServiceType.objects.create(
                provider=request.user,
                name=name,
                duration_minutes=duration_minutes,
                price=price,
            )
            messages.success(request, "نوع خدمت با موفقیت اضافه شد.")
        except Exception as e:
            messages.error(request, f"خطا: {str(e)}")
        return redirect("manage_service_types")
    return render(request, "appointments/add_service_type.html")


@login_required
@require_role([User.RoleChoices.PROVIDER])
def edit_service_type(request, service_type_id):
    """Edit existing service."""
    service = get_object_or_404(ServiceType, id=service_type_id, provider=request.user)
    if request.method == "POST":
        service.name = request.POST.get("name")
        service.duration_minutes = request.POST.get("duration_minutes")
        service.price = request.POST.get("price")
        try:
            service.save()
            messages.success(request, "نوع خدمت با موفقیت ویرایش شد.")
            return redirect("manage_service_types")
        except Exception as e:
            messages.error(request, f"خطا: {str(e)}")
    return render(request, "appointments/edit_service_type.html", {"service": service})


@login_required
@require_role([User.RoleChoices.PROVIDER])
def delete_service_type(request, service_type_id):
    """Delete service (only if no related appointments exist)."""
    service = get_object_or_404(ServiceType, id=service_type_id, provider=request.user)
    if request.method == "POST":
        # Check if any appointment uses this service
        if Appointment.objects.filter(service_type=service).exists():
            messages.error(
                request,
                "این نوع خدمت در نوبت‌های موجود استفاده شده است و قابل حذف نیست.",
            )
        else:
            service.delete()
            messages.success(request, "نوع خدمت با موفقیت حذف شد.")
        return redirect("manage_service_types")
    return render(
        request, "appointments/confirm_delete_service_type.html", {"service": service}
    )