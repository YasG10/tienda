from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from .serializers import OrderSerializer
from .models import Order
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
from django.conf import settings
from .notifications import send_telegram_message
import urllib.request




from .serializers import OrderCreateSerializer
from .services import OrderService


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = OrderService.create_order(
                user=request.user,
                validated_data=serializer.validated_data
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'order_id': order.id},
            status=status.HTTP_201_CREATED
        )

class MyOrdersView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@csrf_exempt
def telegram_webhook(request):
    # Basic webhook receiver for Telegram updates (callback_query handling)
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'ok': False}, status=400)

    # Handle callback_query when inline button pressed
    if 'callback_query' in payload:
        cq = payload['callback_query']
        data = cq.get('data', '')
        from_user = cq.get('from', {})
        callback_id = cq.get('id')

        # Only accept actions from configured admin
        admin_id = getattr(settings, 'TELEGRAM_ADMIN_ID', None)
        if admin_id is None or int(from_user.get('id', 0)) != int(admin_id):
            # answer callback to inform unauthorized
            token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
            if token and callback_id:
                try:
                    url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
                    body = json.dumps({'callback_query_id': callback_id, 'text': 'No autorizado'})
                    req = urllib.request.Request(url, data=body.encode('utf-8'), headers={'Content-Type': 'application/json'})
                    urllib.request.urlopen(req, timeout=5)
                except Exception:
                    pass
            return JsonResponse({'ok': False}, status=403)

        # Parse expected format: order:<id>:<STATUS>
        parts = data.split(':')
        if len(parts) == 3 and parts[0] == 'order':
            try:
                order_id = int(parts[1])
                new_status = parts[2]
            except Exception:
                return JsonResponse({'ok': False}, status=400)

            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                return JsonResponse({'ok': False}, status=404)

            # Validate status
            valid_statuses = {s[0] for s in Order.STATUS_CHOICES}
            if new_status not in valid_statuses:
                return JsonResponse({'ok': False}, status=400)

            order.status = new_status
            order.save()

            token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
            
            # Nombres legibles para los estados
            status_names = {
                'PENDING': '⏳ Pendiente',
                'CONFIRMED': '✅ Confirmado',
                'ON_THE_WAY': '🚚 En Camino',
                'DELIVERED': '📦 Entregado',
                'CANCELLED': '❌ Cancelado'
            }
            status_display = status_names.get(new_status, new_status)
            
            # Responder al callback (quita el loading del botón)
            if token and callback_id:
                try:
                    url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
                    body = json.dumps({'callback_query_id': callback_id, 'text': f'✅ Actualizado a {status_display}'})
                    req = urllib.request.Request(url, data=body.encode('utf-8'), headers={'Content-Type': 'application/json'})
                    urllib.request.urlopen(req, timeout=5)
                except Exception:
                    pass

            # Editar el mensaje original para mostrar el nuevo estado
            if token:
                try:
                    chat_id = cq.get('message', {}).get('chat', {}).get('id')
                    message_id = cq.get('message', {}).get('message_id')
                    
                    if chat_id and message_id:
                        # Escapar caracteres especiales de Markdown
                        def esc(s):
                            if s is None:
                                return ''
                            return str(s).replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
                        
                        # Obtener datos del pedido
                        user = order.user
                        customer_name = esc(user.get_full_name() or user.username)
                        customer_email = esc(getattr(user, 'email', ''))
                        customer_phone = esc(getattr(user, 'phone', '') or getattr(order.address, 'phone', ''))
                        
                        addr = order.address
                        address_lines = []
                        if getattr(addr, 'street', None):
                            address_lines.append(esc(addr.street))
                        if getattr(addr, 'city', None) or getattr(addr, 'province', None):
                            address_lines.append(esc(f"{addr.city}, {addr.province}"))
                        if getattr(addr, 'reference', None):
                            address_lines.append(f"_{esc(addr.reference)}_")
                        
                        items_lines = []
                        for it in order.items.all():
                            name = esc(it.product.name)
                            items_lines.append(f"• {name} x{it.quantity} @ ${it.price}")
                        
                        # Construir mensaje actualizado
                        updated_text = (
                            f"{status_display}\n"
                            f"*Pedido #{order.id}*\n\n"
                            f"👤 *Cliente:* {customer_name}\n"
                            f"📧 {customer_email}\n"
                            f"📱 {customer_phone}\n\n"
                            f"📍 *Dirección:*\n" + "\n".join(address_lines) + "\n\n"
                            f"🛍️ *Items:*\n" + "\n".join(items_lines) + "\n\n"
                            f"💰 *Total:* ${order.total_amount}\n\n"
                            f"_Actualizado: {order.updated_at.strftime('%d/%m/%Y %H:%M')}_"
                        )
                        
                        # Editar el mensaje
                        url = f"https://api.telegram.org/bot{token}/editMessageText"
                        body = json.dumps({
                            'chat_id': chat_id,
                            'message_id': message_id,
                            'text': updated_text,
                            'parse_mode': 'Markdown'
                        })
                        req = urllib.request.Request(url, data=body.encode('utf-8'), headers={'Content-Type': 'application/json'})
                        urllib.request.urlopen(req, timeout=5)
                except Exception:
                    # Si falla editar, no pasa nada. El estado ya se guardó.
                    pass

            return JsonResponse({'ok': True})

    return JsonResponse({'ok': True})