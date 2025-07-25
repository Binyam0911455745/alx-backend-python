# alx-backend-python/messaging_app/chats/auth.py

from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
# from django.contrib.auth.models import User # Use get_user_model if you have custom user model
# from django.contrib.auth import get_user_model
# User = get_user_model()

class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # This is a placeholder to make the file non-empty and valid.
        # Actual authentication is handled by JWTAuthentication and SessionAuthentication.
        return None # Return None to let other authentication classes handle it

    def authenticate_header(self, request):
        return 'x-auth-token'