from django.contrib import admin
from .models import NewsletterSignup, Notification


@admin.register(NewsletterSignup)
class NewsletterSignupAdmin(admin.ModelAdmin):
	list_display = ('email', 'created_at')
	search_fields = ('email',)
	readonly_fields = ('created_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
	list_filter = ('notification_type', 'is_read', 'created_at')
	search_fields = ('user__username', 'title', 'message')
	readonly_fields = ('created_at',)
	list_editable = ('is_read',)
