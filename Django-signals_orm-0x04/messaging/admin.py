#from django.contrib import admin

# Django-signals_orm_0x04/messaging/admin.py

from django.contrib import admin
from .models import Message, Notification, MessageHistory

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp', 'is_read', 'content', 'edited')
    list_filter = ('timestamp', 'is_read', 'sender', 'receiver', 'edited')
    search_fields = ('content', 'sender__username', 'receiver__username')
    date_hierarchy = 'timestamp'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'content', 'timestamp', 'is_read')
    list_filter = ('timestamp', 'is_read', 'user')
    search_fields = ('content', 'user__username')
    date_hierarchy = 'timestamp'

@admin.register(MessageHistory) # <--- NEW ADMIN REGISTRATION
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('message', 'old_content', 'edited_at')
    list_filter = ('edited_at',)
    search_fields = ('message__content', 'old_content')
    date_hierarchy = 'edited_at'

