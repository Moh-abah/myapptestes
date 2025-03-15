from django.http import Http404
from users.models import CustomUser
from messaging.models import Message

def create_message(validated_data, sender):
    # إرسال رسالة جديدة من المرسل إلى المستقبل
    receiver = validated_data['receiver']
    message = Message.objects.create(
        sender=sender,
        receiver=receiver,
        content=validated_data['content']
    )
    return message

def get_merchant_or_404(user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        if user.user_type != 'merchant':
            raise Http404("التاجر غير موجود أو لا ينتمي إلى مجموعة التجار.")
        return user
    except CustomUser.DoesNotExist:
        raise Http404("التاجر غير موجود أو لا ينتمي إلى مجموعة التجار.")
