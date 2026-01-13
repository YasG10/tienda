from django.db import models


class NewsletterSignup(models.Model):
	email = models.EmailField(unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']
		verbose_name = 'Newsletter Signup'
		verbose_name_plural = 'Newsletter Signups'

	def __str__(self):
		return self.email
