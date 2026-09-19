from django.core.exceptions import PermissionDenied


def require_role(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            # Check if user exists first
            if not request.user or not request.user.is_authenticated:
                raise PermissionDenied("You do not have the required permissions.")
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("You do not have the required permissions.")

        return wrapper

    return decorator
