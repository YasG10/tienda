from django.urls import path
from . import web_views
from .views_ofertas import ofertas

app_name = "catalog"

urlpatterns = [
    path('', web_views.home, name='home'),
    path('catalog/', web_views.product_list, name='product_list'),
    path('catalog/product/<int:product_id>/', web_views.product_detail, name='product_detail'),
    path('ofertas/', ofertas, name='ofertas'),
    
    # Autocompletado
    path('api/product-autocomplete/', web_views.product_autocomplete, name='product_autocomplete'),
    
    # URLs de reseñas
    path('catalog/product/<int:product_id>/review/add/', web_views.add_review, name='add_review'),
    path('review/<int:review_id>/edit/', web_views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', web_views.delete_review, name='delete_review'),
    
    # URLs de favoritos
    path('catalog/product/<int:product_id>/favorite/toggle/', web_views.toggle_favorite, name='toggle_favorite'),
    path('my-favorites/', web_views.my_favorites, name='my_favorites'),
]
