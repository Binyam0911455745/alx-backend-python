# messaging_app/chats/urls.py

from django.urls import path
from . import views # Make sure you import your views module

urlpatterns = [
    # Conversation Endpoints
    path('conversations/', views.ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<int:pk>/', views.ConversationRetrieveUpdateDestroyView.as_view(), name='conversation-detail'),

    # Message Endpoints
    # This path is for listing messages within a specific conversation and creating new messages for it.
    # It captures the conversation ID as 'conversation_pk' which the view expects.
    path('conversations/<int:conversation_pk>/messages/', views.MessageListCreateView.as_view(), name='message-list-create'),

    # This path is for retrieving, updating, or deleting a specific message.
    # It uses 'message_pk' as the lookup keyword argument as defined in your view.
    path('messages/<int:message_pk>/', views.MessageRetrieveUpdateDestroyView.as_view(), name='message-detail'),
]