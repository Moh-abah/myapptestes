from ast import Store
from django.db import models
from users.models import CustomUser
from stores.models import Store

# models.py
class Chat(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='customer_chats')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owner_chats')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_chats')  # ربط المحادثة بالمتجر

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('customer', 'owner', 'store')  # ضمان عدم تكرار المحادثات مع نفس العميل والتاجر والمتجر

    def __str__(self):
        
        return f"Chat between {self.customer.username} and {self.owner.username} for {self.store.name_store}"
    

class finalMessage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='mmessages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sentt_messages')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        

        return f"Message from {self.sender.username} in Chat {self.chat.id} at {self.timestamp}: {self.text[:50]}..."  # إضافة التاريخ ونص مختصر للرسالة   
    


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} in Chat {self.chat.id}"
    
 
