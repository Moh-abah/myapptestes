from rest_framework import permissions
from .models import Chat, Message

class IsChatParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # التحقق من أن المستخدم مشارك في المحادثة
        if isinstance(obj, Chat):
            return obj.customer == request.user or obj.merchant == request.user
        elif isinstance(obj, Message):
            return obj.sender == request.user or obj.receiver == request.user
        return False