from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.core.exceptions import PermissionDenied

def user_type_required(required_user_type):
    """
    Decorator to check the user_type of the authenticated user.
    
    :param required_user_type: The required user_type to access the view
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)

            # Check if the user's user_type matches the required user_type
            if user.user_type != required_user_type:
                raise PermissionDenied("You do not have permission to access this resource.")

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
