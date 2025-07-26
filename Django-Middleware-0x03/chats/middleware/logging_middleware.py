# Django-Middleware-0x03/chats/middleware/logging_middleware.py

import logging
from datetime import datetime

# Get an instance of a logger for this module
logger = logging.getLogger(__name__) # __name__ will be 'chats.middleware.logging_middleware'

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the request information using the logger
        user = request.user.username if request.user.is_authenticated else 'AnonymousUser'
        method = request.method
        path = request.path
        timestamp = datetime.now()

        # The message format matches your previous manual logging output
        logger.info(f"{timestamp} - User: {user} - Method: {method} - Path: {path}")

        response = self.get_response(request)
        return response