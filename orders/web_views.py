from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from catalog.models import Product
from .services import OrderService
from addresses.models import Address
from .models import Order
import uuid
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


def _get_cart(request):
    return request.session.setdefault('cart', {})


def cart_view(request):
    cart = _get_cart(request)
    items = []
    total = 0
    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.objects.filter(id__in=product_ids)
    products_map = {p.id: p for p in products}
    for pid, qty in cart.items():
        pid_int = int(pid)
        product = products_map.get(pid_int)
        if not product:
            continue
        items.append({'product': product, 'quantity': qty})
        total += product.price * qty

    return render(request, 'order/cart.html', {'items': items, 'total': total})


@require_POST
def cart_add(request, product_id):
    cart = _get_cart(request)
    pid = str(product_id)
    qty = int(request.POST.get('quantity', 1))
    cart[pid] = cart.get(pid, 0) + qty
    request.session.modified = True
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from catalog.models import Product
        cart_count = sum(cart.values())
        product = Product.objects.get(id=product_id)
        return JsonResponse({
            'success': True,
            'cart_count': cart_count,
            'message': f'{product.name} agregado al carrito',
            'product_name': product.name,
            'quantity': qty
        })
    
    return redirect('orders:cart')


def cart_remove(request, product_id):
    cart = _get_cart(request)
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        request.session.modified = True
    return redirect('orders:cart')


@login_required
def checkout_view(request):
    cart = _get_cart(request)
    if not cart:
        return redirect('orders:cart')

    # Build items from session
    items = []
    for pid, qty in cart.items():
        items.append({'product_id': int(pid), 'quantity': int(qty)})

    # GET: show form with user's addresses
    if request.method == 'GET':
        addresses = Address.objects.filter(user=request.user)
        # If user has no addresses, redirect them to create one
        if not addresses.exists():
            return redirect('addresses:create')
        return render(request, 'order/checkout.html', {'addresses': addresses})

    # POST: attempt to create order using OrderService
    address_id = request.POST.get('address_id')
    notes = request.POST.get('notes', '')

    validated_data = {
        'address_id': int(address_id) if address_id else None,
        'items': items,
        'notes': notes,
    }

    try:
        order = OrderService.create_order(user=request.user, validated_data=validated_data)
    except Exception as e:
        addresses = Address.objects.filter(user=request.user)
        return render(request, 'order/checkout.html', {'addresses': addresses, 'error': str(e)})

    # Clear cart
    request.session['cart'] = {}
    request.session.modified = True

    return redirect('orders:confirmation', order_id=order.id)


@login_required
def confirmation_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order/confirmation.html', {'order': order})


@login_required
def invoice_view(request, order_id):
    # Simple invoice download placeholder: returns a plain text attachment
    order = get_object_or_404(Order, id=order_id, user=request.user)
    lines = []
    lines.append(f"Factura - Orden #{order.id}\n")
    lines.append(f"Fecha: {order.created_at}\n")
    lines.append("Items:\n")
    for it in order.items.all():
        lines.append(f" - {it.product.name} x{it.quantity} @ ${it.price} = ${it.get_subtotal()}\n")
    lines.append(f"\nTotal: ${order.total_amount}\n")
    content = "".join(lines)
    from django.http import HttpResponse
    resp = HttpResponse(content, content_type='text/plain; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="invoice_order_{order.id}.txt"'
    return resp


@login_required
def my_orders_view(request):
    qs = Order.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(qs, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'order/history.html', {'orders': page_obj.object_list, 'page_obj': page_obj})
