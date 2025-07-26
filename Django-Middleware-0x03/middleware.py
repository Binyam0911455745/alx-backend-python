import logging
import time
from datetime import datetime
from django.http import HttpResponseForbidden
from collections import defaultdict


# Configure logging
logging.basicConfig(filename='requests.log', level=logging.INFO)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get user information, if available
        user = request.user if request.user.is_authenticated else 'Anonymous'
        # Log the request details
        logging.info(f"{datetime.now()} - User: {user} - Path: {request.path}")

        # Call the next middleware or view
        response = self.get_response(request)
        return response

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour >= 21:
            return HttpResponseForbidden("Access to the chat is restricted during this time.")
        response = self.get_response(request)
        return response

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.message_count = defaultdict(list)  # Dictionary to track message counts

    def __call__(self, request):
        if request.method == 'POST':
            ip = self.get_client_ip(request)
            current_time = time.time()

            # Clean up old message timestamps
            self.message_count[ip] = [timestamp for timestamp in self.message_count[ip] if current_time - timestamp < 60]

            # Check message count
            if len(self.message_count[ip]) >= 5:
                return HttpResponseForbidden("You have exceeded the limit of 5 messages per minute.")

            # Record the current message timestamp
            self.message_count[ip].append(current_time)

        response = self.get_response(request)
        return response
    def get_client_ip(self, request):
        """ Get the client's IP address from the request """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
