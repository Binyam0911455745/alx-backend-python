# chats/middleware.py

from datetime import datetime
import os
from django.conf import settings

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define the log file path in the project root
        self.log_file_path = os.path.join(settings.BASE_DIR, 'requests.log')

    def __call__(self, request):
        # Code to be executed for each request before the view is called.

        # Get current timestamp
        timestamp = datetime.now()

        # Get the user. If the user is authenticated, use their username.
        # Otherwise, use 'AnonymousUser'.
        user = request.user.username if request.user.is_authenticated else 'AnonymousUser'

        # Get the request path and method
        path = request.path
        method = request.method

        # Construct the log message
        log_message = f"{timestamp} - User: {user} - Method: {method} - Path: {path}\n"

        # Log the information to the 'requests.log' file
        try:
            with open(self.log_file_path, 'a') as f:
                f.write(log_message)
        except IOError as e:
            print(f"Error writing to log file {self.log_file_path}: {e}") # For debugging in console

        # Call the next middleware or the view
        response = self.get_response(request)

        # Code to be executed for each request after the view is called.
        # (For this task, we are primarily logging incoming requests, but this is where
        # you'd add post-response logging if needed, e.g., response.status_code)

        return response