from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.my_conversations, name='my_conversations'),
    path('start/', views.start_conversation, name='start_conversation'),
    path('conversation/<int:pk>/', views.conversation_detail, name='conversation_detail'),
    path('widget/', views.chat_widget, name='chat_widget'),
    
    # APIs AJAX
    path('api/send/<int:conversation_pk>/', views.send_message, name='send_message'),
    path('api/messages/<int:conversation_pk>/', views.get_messages, name='get_messages'),
    path('api/close/<int:pk>/', views.close_conversation, name='close_conversation'),
]
