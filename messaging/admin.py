from django.contrib import admin
from .models import Message,Chat, finalMessage # تأكد من استيراد Message وليس messaging

admin.site.register(Message)
admin.site.register(Chat)
admin.site.register(finalMessage)
