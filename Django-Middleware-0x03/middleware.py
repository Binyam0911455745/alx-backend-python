import logging
from datetime import datetime

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