from django.db.models import Count, Q


def chat_notifications(request):
    """Context processor para notificaciones de chat"""
    try:
        if not hasattr(request, 'user') or not request.user.is_authenticated or not request.user.is_staff:
            return {'unread_chat_count': 0}
        
        # Importar aquí para evitar errores de importación circular
        from chat.models import ChatConversation
        
        # Contar conversaciones con mensajes sin leer para el admin
        unread_count = ChatConversation.objects.filter(
            is_active=True,
            messages__is_read=False
        ).exclude(
            messages__sender=request.user
        ).distinct().count()
        
        return {'unread_chat_count': unread_count}
    except Exception as e:
        # En caso de error, retornar 0 para no romper la página
        return {'unread_chat_count': 0}
