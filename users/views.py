from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.decorators import require_role
from appointments.models import Appointment
from .models import User


@login_required
def profile_edit(request):
    """Edit profile information of logged-in user"""
    if request.method == "POST":
        username = request.POST.get("username")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")

        # Simple validation
        if not username:
            messages.error(request, "نام کاربری نمی‌تواند خالی باشد.")
            return render(request, "users/profile_edit.html", {"user": request.user})

        # Check username uniqueness (except self)
        if User.objects.exclude(pk=request.user.pk).filter(username=username).exists():
            messages.error(request, "این نام کاربری قبلاً ثبت شده است.")
            return render(request, "users/profile_edit.html", {"user": request.user})

        request.user.username = username
        request.user.phone_number = phone_number
        request.user.email = email
        request.user.save()

        messages.success(request, "اطلاعات پروفایل با موفقیت به‌روزرسانی شد.")
        return redirect("users:profile_edit")

    return render(request, "users/profile_edit.html", {"user": request.user})


@login_required
@require_role(["admin"])
def admin_dashboard(request):
    customers = User.objects.filter(
        role=User.RoleChoices.CUSTOMER,
    )
    providers = User.objects.filter(
        role=User.RoleChoices.PROVIDER,
    )
    all_appointments = Appointment.objects.select_related("customer", "provider").all()
    context = {
        "customers": customers,
        "providers": providers,
        "appointments": all_appointments,
    }
    return render(request, "users/admin_dashboard.html", context)


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not username or not email or not password1 or not password2:
            messages.error(request, "تمامی فیلدها الزامی هستند.")
            return render(request, "registration/signup.html")

        if password1 != password2:
            messages.error(request, "رمز عبور و تکرار آن مطابقت ندارند.")
            return render(request, "registration/signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "این نام کاربری قبلاً ثبت شده است.")
            return render(request, "registration/signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "این ایمیل قبلاً ثبت شده است.")
            return render(request, "registration/signup.html")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role="customer",
        )
        login(request, user)
        messages.success(request, f"ثبت نام با موفقیت انجام شد. خوش آمدید {username}!")
        return redirect("customer_dashboard")

    return render(request, "registration/signup.html")


def signup_provider(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email") 
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        phone_number = request.POST.get("phone_number", "")

        if not username or not email or not password1 or not password2:
            messages.error(request, "تمامی فیلدها الزامی هستند.")
            return render(request, "registration/signup_provider.html")

        if password1 != password2:
            messages.error(request, "رمز عبور و تکرار آن مطابقت ندارند.")
            return render(request, "registration/signup_provider.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "این نام کاربری قبلاً ثبت شده است.")
            return render(request, "registration/signup_provider.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "این ایمیل قبلاً ثبت شده است.")
            return render(request, "registration/signup_provider.html")

        user = User.objects.create_user(
            username=username,
            email=email, 
            password=password1,
            role="provider",
            phone_number=phone_number,
        )
        login(request, user)
        messages.success(
            request, f"ثبت نام ارائه‌دهنده با موفقیت انجام شد. خوش آمدید {username}!"
        )
        return redirect("provider_dashboard")

    return render(request, "registration/signup_provider.html")
