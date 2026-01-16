from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import Product, Review, Category
from .forms import ReviewForm
from orders.models import Order, OrderItem


def home(request):
    # Show a hero and a few featured products
    featured = Product.objects.filter(is_active=True, stock__gt=0).order_by('-created_at')[:6]
    return render(request, 'home.html', {
        'featured': featured
    })


def product_list(request):
    qs = Product.objects.filter(is_active=True)

    # Search
    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        qs = qs.filter(category_id=category_id)
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        qs = qs.filter(price__gte=min_price)
    if max_price:
        qs = qs.filter(price__lte=max_price)
    
    # Filter by discount
    has_discount = request.GET.get('has_discount')
    if has_discount == '1':
        qs = qs.filter(discount_percent__gt=0)
    
    # Only available products by default (unless user wants to see all)
    show_all = request.GET.get('show_all')
    if not show_all:
        qs = qs.filter(stock__gt=0)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    
    # Validate and apply sorting
    valid_sorts = {
        'price_asc': 'price',
        'price_desc': '-price',
        'name_asc': 'name',
        'name_desc': '-name',
        'newest': '-created_at',
        'oldest': 'created_at',
        'popular': '-id',  # We'll use review count for popularity
    }
    
    if sort_by == 'popular':
        # Sort by number of reviews (popularity)
        qs = qs.annotate(review_count=Count('reviews')).order_by('-review_count', '-created_at')
    else:
        sort_field = valid_sorts.get(sort_by, '-created_at')
        qs = qs.order_by(sort_field)

    # Get all categories for filter
    categories = Category.objects.filter(is_active=True).annotate(
        product_count=Count('products', filter=Q(products__is_active=True, products__stock__gt=0))
    ).filter(product_count__gt=0)

    # Pagination
    page_size = 12
    paginator = Paginator(qs, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'catalog/product_list.html', {
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'query': q,
        'categories': categories,
        'selected_category': category_id,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'has_discount': has_discount,
        'sort_by': sort_by,
    })


def product_autocomplete(request):
    """Endpoint para autocompletado de búsqueda"""
    q = request.GET.get('q', '').strip()
    
    if len(q) < 2:
        return JsonResponse({'suggestions': []})
    
    products = Product.objects.filter(
        Q(name__icontains=q) | Q(description__icontains=q),
        is_active=True,
        stock__gt=0
    )[:8]
    
    suggestions = []
    for product in products:
        suggestions.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'image': product.image.url if product.image else None,
            'url': f'/catalog/product/{product.id}/'
        })
    
    return JsonResponse({'suggestions': suggestions})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Obtener reseñas aprobadas
    reviews = product.reviews.filter(is_approved=True).select_related('user').order_by('-created_at')
    
    # Verificar si el usuario puede dejar una reseña
    user_can_review = False
    user_has_reviewed = False
    user_review = None
    
    if request.user.is_authenticated:
        # Verificar si ya dejó una reseña
        user_review = product.reviews.filter(user=request.user).first()
        user_has_reviewed = user_review is not None
        
        # Verificar si ha comprado el producto
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__status=Order.STATUS_DELIVERED
        ).exists()
        
        user_can_review = has_purchased and not user_has_reviewed
    
    # Formulario de reseña
    review_form = ReviewForm() if user_can_review else None
    
    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'user_can_review': user_can_review,
        'user_has_reviewed': user_has_reviewed,
        'user_review': user_review,
        'review_form': review_form,
    })


@login_required
def add_review(request, product_id):
    """Vista para agregar una reseña"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Verificar si ya dejó una reseña
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.warning(request, 'Ya has dejado una reseña para este producto.')
        return redirect('catalog:product_detail', product_id=product_id)
    
    # Verificar si ha comprado el producto
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__status=Order.STATUS_DELIVERED
    ).exists()
    
    if not has_purchased:
        messages.error(request, 'Solo puedes dejar reseñas en productos que hayas comprado.')
        return redirect('catalog:product_detail', product_id=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.verified_purchase = True
            review.save()
            messages.success(request, '¡Gracias por tu reseña! Ha sido publicada.')
            return redirect('catalog:product_detail', product_id=product_id)
    else:
        form = ReviewForm()
    
    return render(request, 'catalog/add_review.html', {
        'form': form,
        'product': product
    })


@login_required
def edit_review(request, review_id):
    """Vista para editar una reseña"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu reseña ha sido actualizada.')
            return redirect('catalog:product_detail', product_id=review.product.id)
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'catalog/edit_review.html', {
        'form': form,
        'review': review,
        'product': review.product
    })


@login_required
def delete_review(request, review_id):
    """Vista para eliminar una reseña"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_id = review.product.id
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Tu reseña ha sido eliminada.')
        return redirect('catalog:product_detail', product_id=product_id)
    
    return render(request, 'catalog/delete_review.html', {
        'review': review
    })


@login_required
def toggle_favorite(request, product_id):
    """Vista para agregar/quitar producto de favoritos"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    product = get_object_or_404(Product, id=product_id)
    user = request.user
    
    if product in user.favorite_products.all():
        user.favorite_products.remove(product)
        is_favorite = False
        message = f'{product.name} eliminado de favoritos'
    else:
        user.favorite_products.add(product)
        is_favorite = True
        message = f'{product.name} agregado a favoritos'
    
    favorites_count = user.favorite_products.count()
    
    return JsonResponse({
        'success': True,
        'is_favorite': is_favorite,
        'message': message,
        'favorites_count': favorites_count
    })


@login_required
def my_favorites(request):
    """Vista para mostrar los productos favoritos del usuario"""
    favorites = request.user.favorite_products.filter(is_active=True)
    
    paginator = Paginator(favorites, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'catalog/my_favorites.html', {
        'favorites': page_obj,
        'total_favorites': favorites.count()
    })
