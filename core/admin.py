from django.contrib import admin
from .models import NewsletterSignup


@admin.register(NewsletterSignup)
class NewsletterSignupAdmin(admin.ModelAdmin):
	list_display = ('email', 'created_at')
	search_fields = ('email',)
	readonly_fields = ('created_at',)
