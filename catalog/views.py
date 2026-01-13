from rest_framework import generics
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True, stock__gt=0)
    serializer_class = ProductSerializer
