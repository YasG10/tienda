from django.shortcuts import render


from catalog.models import Product
from django.shortcuts import redirect
from .forms import NewsletterSignupForm
from django.contrib import messages
from django.db import IntegrityError


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
