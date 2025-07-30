#from django.contrib import admin

# Django-signals_orm_0x04/messaging/admin.py

from django.contrib import admin
from .models import Message, Notification

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp', 'is_read', 'content')
    list_filter = ('timestamp', 'is_read', 'sender', 'receiver')
    search_fields = ('content', 'sender__username', 'receiver__username')
    date_hierarchy = 'timestamp'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'content', 'timestamp', 'is_read')
    list_filter = ('timestamp', 'is_read', 'user')
    search_fields = ('content', 'user__username')
    date_hierarchy = 'timestamp'
