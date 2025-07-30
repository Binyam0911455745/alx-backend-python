# Django-signals_orm-0x04/Django_signals_orm_0x04/urls.py

from django.contrib import admin
from django.urls import path, include
from messaging.views import MessageDetailWithHistoryView, MessageHistoryListView, DeleteUserAccountView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Existing API endpoints
    path('api/messages/<int:pk>/', MessageDetailWithHistoryView.as_view(), name='message-detail-with-history'),
    path('api/messages/<int:message_pk>/history/', MessageHistoryListView.as_view(), name='message-history-list'),

    # NEW URL for user deletion
    path('api/delete-my-account/', DeleteUserAccountView.as_view(), name='delete-my-account'), # <--- ENSURE THIS COMMA IS HERE
]