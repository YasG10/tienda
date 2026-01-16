from django.contrib import admin
from .models import ChatConversation, ChatMessage


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('sender', 'message', 'created_at', 'is_read')
    can_delete = False


class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'is_active', 'is_resolved', 'unread_count')
    list_filter = ('is_active', 'is_resolved', 'created_at')
    search_fields = ('user__username', 'user__email')
    inlines = [ChatMessageInline]
    
    def unread_count(self, obj):
        return obj.messages.filter(is_read=False).exclude(sender=obj.user).count()
    unread_count.short_description = 'Mensajes sin leer'


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'message_preview', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('message', 'sender__username')
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Mensaje'


admin.site.register(ChatConversation, ChatConversationAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)

