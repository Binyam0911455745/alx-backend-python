# messaging_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Add this line
    # other URL patterns
]