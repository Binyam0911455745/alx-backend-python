from django.urls import path, include
from django.contrib import admin
from . import views  # Import your views.py file

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # This is the new line
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('chats.api.urls')),
]