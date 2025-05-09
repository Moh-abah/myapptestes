from django.urls import include, path

from messaging.views import ChatDetailView, ChatttDetailView, ChattttnewListCreateView, CheckOrCreateChatView,  MessageDetailView, MessageListCreateView, RetrieveChatsAPIView, SendMessageView, GetMessagesWithMerchantView, GetConversationsView, CreateChatView,  finalCreateChatAPIView


urlpatterns = [
    # عرض المحادثات
    #path('chats/', GetConversationsView.as_view(), name='get_conversations'),
    
    # عرض الرسائل مع التاجر
    path('chats/<int:merchant_id>/getma/', GetMessagesWithMerchantView.as_view(), name='get_messages_with_merchant'),
    
    # إنشاء محادثة جديدة
    path('chats/create/', CreateChatView.as_view(), name='create_chat'),
    
    # إرسال رسالة إلى المحادثة
    path('chats/<int:chat_id>/messages/', SendMessageView.as_view(), name='send_message'),

    path('chats/check-or-create-chat/', CheckOrCreateChatView.as_view(), name='check_or_create_chat'),
    
    path('chatsssss/', ChattttnewListCreateView.as_view(), name='chat-list-create'),
    path('chats/<int:pk>/', ChatDetailView.as_view(), name='chat-detail'),

    # URLs للرسائل
    path('messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/<int:chat_id>/', MessageListCreateView.as_view(), name='message-list-by-chat'),
    path('messages/detail/<int:pk>/', MessageDetailView.as_view(), name='message-detail'),

    path('chatss/<int:chat_id>/', ChatttDetailView.as_view(), name='chat_detail'),

    path('chatssss/<int:chat_id>/', ChatDetailView.as_view(), name='chat-detail'),



    path('finalcreate-chat/', finalCreateChatAPIView.as_view(), name='create-chat'),
    path('getchats/', RetrieveChatsAPIView.as_view(), name='getts-chat'),
  


    
    
]



