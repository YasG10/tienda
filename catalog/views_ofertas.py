from django.shortcuts import render
from catalog.models import Product

def ofertas(request):
    productos = Product.objects.filter(is_active=True, discount_percent__gt=0)
    return render(request, 'ofertas.html', {'productos': productos})
