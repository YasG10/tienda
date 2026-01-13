from django.urls import path
from . import web_views

app_name = 'orders'

urlpatterns = [
    path('', web_views.cart_view, name='cart'),
    path('add/<int:product_id>/', web_views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', web_views.cart_remove, name='cart_remove'),
    path('checkout/', web_views.checkout_view, name='checkout'),
    path('confirmation/<int:order_id>/', web_views.confirmation_view, name='confirmation'),
    path('my/', web_views.my_orders_view, name='my_orders'),
    path('invoice/<int:order_id>/', web_views.invoice_view, name='invoice'),
]
