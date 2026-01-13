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

            # Acknowledge callback and notify admin
            token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
            if token and callback_id:
                try:
                    url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
                    body = json.dumps({'callback_query_id': callback_id, 'text': f'Estado cambiado a {new_status}'})
                    req = urllib.request.Request(url, data=body.encode('utf-8'), headers={'Content-Type': 'application/json'})
                    urllib.request.urlopen(req, timeout=5)
                except Exception:
                    pass

            # send confirmation message
            admin_chat = getattr(settings, 'TELEGRAM_ADMIN_ID', None)
            if admin_chat:
                send_telegram_message(admin_chat, f'Orden #{order.id} ahora: {order.status}')

            return JsonResponse({'ok': True})

    return JsonResponse({'ok': True})