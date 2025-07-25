# chats/middleware.py

from datetime import datetime, time, timedelta # Added timedelta for OffensiveLanguageMiddleware
import os # Import os to construct the file path reliably
from django.conf import settings # To get the BASE_DIR setting
from django.http import HttpResponseForbidden # Import HttpResponseForbidden for blocking responses

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
        # Define the log file path, relative to BASE_DIR
        self.log_file_path = os.path.join(settings.BASE_DIR, 'requests.log')

    def __call__(self, request):
        # Code to be executed for each request before the view is called.

        # Get current timestamp
        timestamp = datetime.now()

        # Get the user. If the user is authenticated, use their username.
        # Otherwise, use 'AnonymousUser'.
        user = request.user.username if request.user.is_authenticated else 'AnonymousUser'

        # Get the request path
        path = request.path

        # Construct the log message
        log_message = f"{timestamp} - User: {user} - Path: {path}\n"

        # Log the information to the 'requests.log' file
        try:
            with open(self.log_file_path, 'a') as f:
                f.write(log_message)
        except IOError as e:
            # In a real application, you'd use Django's logging system
            # for errors like this, but for this exercise, print to console.
            print(f"Error writing to log file {self.log_file_path}: {e}")

        # Call the next middleware or the view
        response = self.get_response(request)

        # Code to be executed for each request after the view is called.
        # (For this task, we don't need post-response logging, but it's where it would go)

        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define allowed access hours (6 AM to 9 PM)
        self.start_time = time(6, 0, 0)  # 6 AM
        self.end_time = time(21, 0, 0)  # 9 PM (21:00)

    def __call__(self, request):
        # Get the current time
        now = datetime.now().time()

        # Check if the current time is outside the allowed window (6 AM to 9 PM)
        # Meaning, if it's between 9 PM (inclusive) and 6 AM (exclusive)
        if not (self.start_time <= now < self.end_time):
            # Access is denied
            return HttpResponseForbidden("Access to chat is restricted between 9 PM and 6 AM EAT.")

        # If within the allowed time, proceed with the request
        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware:
    # This dictionary will store timestamps of POST requests for each IP address.
    # It's a class variable so it's shared across all instances of the middleware.
    # In a production environment, you would use a proper caching system (like Redis)
    # as this will reset if the server restarts and won't scale across multiple processes.
    requests_per_ip = {}
    MAX_MESSAGES_PER_MINUTE = 5
    TIME_WINDOW_MINUTES = 1

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # We only care about POST requests as they typically represent sending messages
        if request.method == 'POST':
            # Get the client's IP address
            # Use X-Forwarded-For if behind a proxy, otherwise REMOTE_ADDR
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            current_time = datetime.now()

            # Initialize list for this IP if it's the first time we see it
            if ip_address not in self.requests_per_ip:
                self.requests_per_ip[ip_address] = []

            # Clean up old requests (older than TIME_WINDOW_MINUTES)
            # This ensures only recent requests contribute to the count
            self.requests_per_ip[ip_address] = [
                t for t in self.requests_per_ip[ip_address]
                if current_time - t <= timedelta(minutes=self.TIME_WINDOW_MINUTES)
            ]

            # Check if the limit is exceeded
            if len(self.requests_per_ip[ip_address]) >= self.MAX_MESSAGES_PER_MINUTE:
                return HttpResponseForbidden(
                    f"You have exceeded the message limit ({self.MAX_MESSAGES_PER_MINUTE} messages per {self.TIME_WINDOW_MINUTES} minute). Please try again later."
                )
            else:
                # Add the current request's timestamp to the list
                self.requests_per_ip[ip_address].append(current_time)

        # Process the request if not blocked, or if it's not a POST request
        response = self.get_response(request)
        return response


class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define URL prefixes that require admin/moderator permissions
        # By default, we'll restrict access to the Django admin panel
        self.restricted_admin_paths = ['/admin/']

    def __call__(self, request):
        # Check if the requested path starts with any of the restricted admin paths
        is_restricted_path = False
        for path_prefix in self.restricted_admin_paths:
            if request.path.startswith(path_prefix):
                is_restricted_path = True
                break

        if is_restricted_path:
            # If it's a restricted path, check user's role
            # Users must be authenticated AND either staff or superuser
            # is_staff covers both regular staff users and superusers.
            if not request.user.is_authenticated or not request.user.is_staff:
                return HttpResponseForbidden("You do not have the necessary administrative/moderator permissions to access this page.")

        # If it's not a restricted path, or if the user has permission,
        # proceed with the request.
        response = self.get_response(request)
        return response