# Django-Middleware-0x03/chats/middleware/restrict_by_time.py

from datetime import datetime
from django.http import HttpResponseForbidden

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the current time
        current_hour = datetime.now().hour # datetime.now() uses the local timezone if not specified
                                           # For consistent behavior across timezones, consider using
                                           # django.utils.timezone.now().hour if you configure USE_TZ = True
                                           # and TIME_ZONE correctly in settings.py.
                                           # Currently, it relies on the system's local time.


        # Access is restricted between 9 PM (21:00) and 6 AM (06:00).
        # So, if current_hour is 0, 1, 2, 3, 4, 5, 21, 22, 23.
        if current_hour < 6 or current_hour >= 21:
            return HttpResponseForbidden("Access to the chat is restricted between 9 PM and 6 AM EAT.")

        # If within allowed hours, call the next middleware or view
        response = self.get_response(request)
        return response