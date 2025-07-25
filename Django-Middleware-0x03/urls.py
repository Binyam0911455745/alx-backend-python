# alx-backend-python/messaging_app/messaging_app/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter # Import DefaultRouter

# Import JWT views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Import views from your chats app
from chats import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
# Register ConversationViewSet with the router
router.register(r'conversations', views.ConversationViewSet, basename='conversation')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')), # For optional browsable API login/logout

    # Include API routes from the router (for ConversationViewSet)
    path('api/', include(router.urls)),

    # Explicitly define paths for MessageList and MessageDetail
    # These are nested under conversations using the conversation_pk
    path('api/conversations/<uuid:conversation_pk>/messages/', views.MessageList.as_view(), name='message-list'),
    path('api/conversations/<uuid:conversation_pk>/messages/<uuid:message_id>/', views.MessageDetail.as_view(), name='message-detail'),

    # JWT Authentication Endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]