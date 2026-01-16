from django.db import models
from django.conf import settings


class NewsletterSignup(models.Model):
	email = models.EmailField(unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']
		verbose_name = 'Newsletter Signup'
		verbose_name_plural = 'Newsletter Signups'

	def __str__(self):
		return self.email


class Notification(models.Model):
	NOTIFICATION_TYPES = [
		('order_status', 'Cambio de estado de pedido'),
		('new_message', 'Nuevo mensaje'),
		('system', 'Notificación del sistema'),
		('promotion', 'Promoción especial'),
	]
	
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
	notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
	title = models.CharField(max_length=200)
	message = models.TextField()
	link = models.CharField(max_length=500, blank=True, null=True)
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		ordering = ['-created_at']
		verbose_name = 'Notificación'
		verbose_name_plural = 'Notificaciones'
	
	def __str__(self):
		return f"{self.user.username} - {self.title}"
