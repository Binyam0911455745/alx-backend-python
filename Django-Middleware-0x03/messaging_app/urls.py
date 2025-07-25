# alx-backend-python/messaging_app/messaging_app/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers # <--- Import routers

# Import JWT views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Assuming you have views in chats.views now. Import them
from chats import views as chats_views

# Initialize DRF router for ViewSets
router = routers.DefaultRouter()
router.register(r'messages', chats_views.MessageViewSet, basename='message') # Register MessageViewSet
router.register(r'conversations', chats_views.ConversationViewSet, basename='conversation') # Register ConversationViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)), # Use router for API paths

    # JWT Authentication Endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]