from django.db import models
from django.conf import settings
from django.utils import timezone


class ChatConversation(models.Model):
    """Conversación de chat entre un cliente y un administrador"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_resolved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Conversación'
        verbose_name_plural = 'Conversaciones'
    
    def __str__(self):
        return f"Chat con {self.user.username} - {self.created_at.strftime('%d/%m/%Y')}"
    
    def get_unread_count_for_user(self, user):
        """Obtener mensajes no leídos para un usuario específico"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()
    
    def get_last_message(self):
        """Obtener el último mensaje de la conversación"""
        return self.messages.order_by('-created_at').first()


class ChatMessage(models.Model):
    """Mensaje individual en una conversación"""
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
    
    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Actualizar el timestamp de la conversación
        self.conversation.updated_at = timezone.now()
        self.conversation.save(update_fields=['updated_at'])

