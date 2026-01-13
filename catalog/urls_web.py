from django.urls import path
from . import web_views
from .views_ofertas import ofertas

app_name = "catalog"

urlpatterns = [
    path('', web_views.home, name='home'),
    path('catalog/', web_views.product_list, name='product_list'),
    path('catalog/product/<int:product_id>/', web_views.product_detail, name='product_detail'),
    path('ofertas/', ofertas, name='ofertas'),
]
