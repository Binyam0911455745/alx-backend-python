# chats/middleware.py

from datetime import datetime, time
import os # Import os to construct the file path reliably
from django.conf import settings # To get the BASE_DIR setting
from django.http import HttpResponseForbidden

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
        # Define allowed access hours
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

