from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Product


def home(request):
    # Show a hero and a few featured products
    featured = Product.objects.filter(is_active=True, stock__gt=0).order_by('-created_at')[:6]
    return render(request, 'home.html', {
        'featured': featured
    })


def product_list(request):
    qs = Product.objects.filter(is_active=True)

    # Search
    q = request.GET.get('q')
    if q:
        qs = qs.filter(name__icontains=q) | qs.filter(description__icontains=q)

    # Only available products by default
    qs = qs.filter(stock__gt=0)

    # Pagination
    page_size = 9
    paginator = Paginator(qs.order_by('-created_at'), page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'catalog/product_list.html', {
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'query': q,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    return render(request, 'catalog/product_detail.html', {
        'product': product
    })
