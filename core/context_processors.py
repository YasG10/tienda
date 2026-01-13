def cart_count(request):
    """Return number of items in the session cart."""
    cart = request.session.get('cart', {})
    try:
        count = sum(int(q) for q in cart.values())
    except Exception:
        count = 0
    return {'cart_item_count': count}
