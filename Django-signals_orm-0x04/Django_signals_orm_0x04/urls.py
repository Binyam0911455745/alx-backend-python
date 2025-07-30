# Django-signals_orm_0x04/urls.py

from django.contrib import admin
from django.urls import path, include
#from django.views.decorators.cache import cache_page
from messaging.views import (
    MessageDetailWithHistoryView,
    MessageHistoryListView,
    DeleteUserAccountView,
    MessageCreateView,      # <--- ADDED for creating messages/replies
    ThreadedMessageListView, # <--- ADDED for listing threaded conversations
    UnreadMessageListView
)

# Define the cache timeout in seconds
#CACHE_TIMEOUT = 60 # As per instruction: 60 seconds

urlpatterns = [
    path('admin/', admin.site.urls),
    # Authentication URLs (if you're using Djoser or similar)
    # path('api/auth/', include('djoser.urls')),
    # path('api/auth/', include('djoser.urls.jwt')), # For JWT auth

    # Message-related URLs
    path('api/messages/', ThreadedMessageListView.as_view(), name='message-list-threaded'), # For listing top-level threaded messages
    path('api/messages/create/', MessageCreateView.as_view(), name='message-create'), # For creating new messages
    path('api/messages/unread/', UnreadMessageListView.as_view(), name='message-list-unread'), # <--- ADDED URL for unread messages
    path('api/messages/<int:pk>/', MessageDetailWithHistoryView.as_view(), name='message-detail-with-history'),
    path('api/messages/<int:message_pk>/history/', MessageHistoryListView.as_view(), name='message-history-list'),

    # User account deletion
    path('api/users/delete-my-account/', DeleteUserAccountView.as_view(), name='delete-my-account'),
]