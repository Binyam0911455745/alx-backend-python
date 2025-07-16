from django.contrib import admin

# Register your models here.
from .models import User, Conversation, Message # Import your models

# Register your models here.
admin.site.register(User)
admin.site.register(Conversation)
admin.site.register(Message)