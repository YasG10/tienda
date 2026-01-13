from django.db import transaction
from django.shortcuts import get_object_or_404

from catalog.models import Product
from addresses.models import Address
from .models import Order, OrderItem


class OrderService:

    @staticmethod
    @transaction.atomic
    def create_order(user, validated_data):
        address = get_object_or_404(Address, id=validated_data['address_id'], user=user)

        order = Order.objects.create(
            user=user,
            address=address,
            notes=validated_data.get('notes', '')
        )

        total = 0

        for item in validated_data['items']:
            product = get_object_or_404(Product, id=item['product_id'], is_active=True)

            if product.stock < item['quantity']:
                raise ValueError(f"Stock insuficiente para {product.name}")

            product.stock -= item['quantity']
            product.save()

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price=product.price
            )

            total += product.price * item['quantity']

        order.total_amount = total
        order.save()

        # Notify admin via Telegram (best-effort; will not raise on failure)
        try:
            from .notifications import notify_admin_order
            notify_admin_order(order)
        except Exception:
            # If notifications fail, continue silently
            pass

        return order
