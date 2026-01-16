from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from catalog.models import Product
from django.shortcuts import redirect
from .forms import NewsletterSignupForm
from django.contrib import messages
from django.db import IntegrityError
from .models import Notification


def newsletter_signup(request):
	if request.method == 'POST':
		form = NewsletterSignupForm(request.POST)
		if form.is_valid():
			try:
				form.save()
				messages.success(request, 'Gracias por suscribirte. Te avisaremos por correo.')
			except IntegrityError:
				messages.info(request, 'Ya estás suscrito con ese correo.')
		else:
			messages.error(request, 'Por favor, introduce un correo válido.')
	return redirect('home')


# Landing / home view
def landing(request):
	"""Render the marketing landing page as the new home."""
	featured_products = Product.objects.filter(is_active=True)[:8]
	return render(request, 'landing.html', {
		'featured_products': featured_products,
	})


# Custom 404 handler
def custom_404(request, exception):
	"""Handle 404 errors and render custom 404 page."""
	return render(request, '404.html', status=404)


# Notification API
@login_required
def notifications_list(request):
	"""Get all notifications for current user."""
	notifications = Notification.objects.filter(user=request.user)[:20]
	unread_count = notifications.filter(is_read=False).count()
	
	data = {
		'notifications': [{
			'id': n.id,
			'type': n.notification_type,
			'title': n.title,
			'message': n.message,
			'link': n.link,
			'is_read': n.is_read,
			'created_at': n.created_at.strftime('%d/%m/%Y %H:%M'),
		} for n in notifications],
		'unread_count': unread_count,
	}
	
	return JsonResponse(data)


@login_required
@require_POST
def notification_mark_read(request, notification_id):
	"""Mark a notification as read."""
	try:
		notification = Notification.objects.get(id=notification_id, user=request.user)
		notification.is_read = True
		notification.save()
		return JsonResponse({'success': True})
	except Notification.DoesNotExist:
		return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)


@login_required
@require_POST
def notification_mark_all_read(request):
	"""Mark all notifications as read."""
	Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
	return JsonResponse({'success': True})
