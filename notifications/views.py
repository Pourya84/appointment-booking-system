from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification


@login_required
def notification_list(request):
    notifications = request.user.notifications.all()
    return render(request, "notifications/list.html", {"notifications": notifications})


@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(
        Notification, id=notification_id, user=request.user
    )
    notification.is_read = True
    notification.save()
    messages.success(request, "پیام به عنوان خوانده شده علامت‌گذاری شد.")
    return redirect("notifications:notification_list")


@login_required
def mark_all_as_read(request):
    """Mark all user notifications as read"""
    if request.method == "POST":
        # Update all unread notifications for the user
        updated_count = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
        messages.success(
            request, f"{updated_count} پیام به عنوان خوانده شده علامت‌گذاری شد."
        )
    else:
        messages.error(request, "درخواست نامعتبر است.")
    return redirect("notifications:notification_list")
