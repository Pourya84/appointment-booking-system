from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from appointments.views_html import home_view
from users.views import signup
from django.conf import settings
from django.conf.urls.static import static

# ======================== Swagger Configuration ========================
schema_view = get_schema_view(
    openapi.Info(
        title="Appointment Booking System - API Documentation",
        default_version="v1.0.0",
        description="Complete API documentation for the appointment booking project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # ======== Home Page ========
    path("", home_view, name="home"),
    # ======== Admin & Auth ========
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    # ======== App URLs ========
    path("", include("users.urls")),
    path(
        "", include("appointments.urls")
    ),  # <-- FIXED: استفاده از appointments.urls (HTML views)
    path("notifications/", include("notifications.urls")),
    # ======== API v1 ========
    path("api/v1/", include("appointments.api.v1.urls")),
    # ======== Swagger Documentation ========
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
]
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
