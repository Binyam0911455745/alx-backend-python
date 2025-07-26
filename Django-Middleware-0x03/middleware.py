import logging
from datetime import datetime
from django.http import HttpResponseForbidden

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

