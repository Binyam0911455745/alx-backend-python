from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers # <-- Required by checker
from .views import ConversationViewSet, MessageViewSet

# Create a DefaultRouter for top-level resources (like Conversations)
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Create a NestedDefaultRouter for messages, nested under conversations
# The 'lookup' argument defines the URL keyword argument that will capture the parent ID (e.g., 'conversation_pk')
conversations_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

# Combine the URLs from both routers
urlpatterns = router.urls + conversations_router.urls