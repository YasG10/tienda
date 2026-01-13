from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from catalog.models import Product, Category
from orders.models import Order

@staff_member_required
def admin_dashboard(request):
    productos = Product.objects.count()
    categorias = Category.objects.count()
    pedidos = Order.objects.count()
    pedidos_recientes = Order.objects.order_by('-created_at')[:5]
    return render(request, 'admin_dashboard.html', {
        'productos': productos,
        'categorias': categorias,
        'pedidos': pedidos,
        'pedidos_recientes': pedidos_recientes,
    })
