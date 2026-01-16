from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from .models import ChatConversation, ChatMessage


@login_required
def chat_widget(request):
    """Widget de chat flotante para clientes"""
    # Obtener o crear conversación activa para el usuario
    conversation = ChatConversation.objects.filter(
        user=request.user, 
        is_active=True
    ).first()
    
    return render(request, 'chat/widget.html', {
        'conversation': conversation
    })


@login_required
def start_conversation(request):
    """Iniciar una nueva conversación de chat"""
    conversation, created = ChatConversation.objects.get_or_create(
        user=request.user,
        is_active=True,
        defaults={'is_resolved': False}
    )
    
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        if message_text:
            ChatMessage.objects.create(
                conversation=conversation,
                sender=request.user,
                message=message_text
            )
    
    return redirect('chat:conversation_detail', pk=conversation.pk)


@login_required
def conversation_detail(request, pk):
    """Vista detallada de una conversación"""
    conversation = get_object_or_404(ChatConversation, pk=pk)
    
    # Verificar permisos
    if not request.user.is_staff and conversation.user != request.user:
        return redirect('chat:my_conversations')
    
    # Marcar mensajes como leídos
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        if message_text:
            ChatMessage.objects.create(
                conversation=conversation,
                sender=request.user,
                message=message_text
            )
            return redirect('chat:conversation_detail', pk=pk)
    
    messages = conversation.messages.all()
    
    return render(request, 'chat/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages
    })


@login_required
def my_conversations(request):
    """Lista de conversaciones del usuario"""
    if request.user.is_staff:
        # Admin ve todas las conversaciones
        conversations = ChatConversation.objects.all().annotate(
            unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user))
        )
    else:
        # Cliente ve solo sus conversaciones
        conversations = ChatConversation.objects.filter(user=request.user)
    
    return render(request, 'chat/conversation_list.html', {
        'conversations': conversations
    })


@login_required
def send_message(request, conversation_pk):
    """API para enviar mensajes vía AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    conversation = get_object_or_404(ChatConversation, pk=conversation_pk)
    
    # Verificar permisos
    if not request.user.is_staff and conversation.user != request.user:
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    message_text = request.POST.get('message', '').strip()
    if not message_text:
        return JsonResponse({'error': 'Mensaje vacío'}, status=400)
    
    message = ChatMessage.objects.create(
        conversation=conversation,
        sender=request.user,
        message=message_text
    )
    
    return JsonResponse({
        'success': True,
        'message': {
            'id': message.id,
            'sender': message.sender.username,
            'sender_id': message.sender.id,
            'message': message.message,
            'created_at': message.created_at.strftime('%H:%M'),
            'is_staff': message.sender.is_staff
        }
    })


@login_required
def get_messages(request, conversation_pk):
    """API para obtener mensajes nuevos vía AJAX"""
    conversation = get_object_or_404(ChatConversation, pk=conversation_pk)
    
    # Verificar permisos
    if not request.user.is_staff and conversation.user != request.user:
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    since_id = request.GET.get('since', 0)
    messages = conversation.messages.filter(id__gt=since_id)
    
    # Marcar como leídos los mensajes que no son del usuario actual
    messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    messages_data = [{
        'id': msg.id,
        'sender': msg.sender.username,
        'sender_id': msg.sender.id,
        'message': msg.message,
        'created_at': msg.created_at.strftime('%H:%M'),
        'is_staff': msg.sender.is_staff
    } for msg in messages]
    
    return JsonResponse({
        'messages': messages_data,
        'unread_count': conversation.get_unread_count_for_user(request.user)
    })


@login_required
def close_conversation(request, pk):
    """Cerrar/resolver una conversación"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    conversation = get_object_or_404(ChatConversation, pk=pk)
    conversation.is_resolved = True
    conversation.is_active = False
    conversation.save()
    
    return JsonResponse({'success': True})

