from rest_framework import serializers
from .models import Order, OrderItem
from catalog.models import Product
from addresses.models import Address


class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    items = OrderItemCreateSerializer(many=True)
    notes = serializers.CharField(required=False, allow_blank=True)

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['product_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'total_amount', 'items', 'created_at']