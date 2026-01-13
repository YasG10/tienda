import json
import urllib.request
import urllib.parse
from django.conf import settings
import ssl


def send_telegram_message(chat_id, text):
    """Send a simple text message via Telegram Bot API. If TELEGRAM_BOT_TOKEN is not set, this is a no-op.

    Uses urllib to avoid external dependencies.
    """
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not token:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    encoded = urllib.parse.urlencode(data).encode('utf-8')

    try:
        req = urllib.request.Request(url, data=encoded)
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_data = resp.read().decode('utf-8')
            result = json.loads(resp_data)
            return result.get('ok', False)
    except Exception:
        # Do not raise from notification failure; log could be added
        return False


def send_telegram_with_markup(payload: dict):
    """Send a JSON payload to the Telegram sendMessage endpoint. Payload should include token in URL usage."""
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not token:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        # Allow TLS even if system lacks proper CA in some environments
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            resp_data = resp.read().decode('utf-8')
            result = json.loads(resp_data)
            return result.get('ok', False)
    except Exception:
        return False


def notify_admin_order(order):
    """Compose and send a notification about a newly created order to the configured admin."""
    admin_id = getattr(settings, 'TELEGRAM_ADMIN_ID', None)
    if not admin_id:
        return False

    def esc(s):
        # Simple escape for Markdown (basic) to avoid formatting injection
        if s is None:
            return ''
        return str(s).replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')

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
        address_lines.append(esc(addr.reference))

    items_lines = []
    for it in order.items.all():
        name = esc(it.product.name)
        qty = it.quantity
        price = it.price
        subtotal = it.get_subtotal()
        items_lines.append(f"- {name} x{qty} @ ${price} = ${subtotal}")

    text = (
        f"📦 *Nuevo pedido*\n"
        f"*ID:* {order.id}\n"
        f"*Usuario:* {customer_name}\n"
        f"*Email:* {customer_email}\n"
        f"*Tel:* {customer_phone}\n"
        f"*Dirección de entrega:*\n" + "\n".join(address_lines) + "\n"
        f"*Items:*\n" + "\n".join(items_lines) + "\n"
        f"*Total a pagar:* ${order.total_amount}"
    )

    # Build inline keyboard for status actions
    keyboard = [
        [
            {"text": "Confirmar pedido", "callback_data": f"order:{order.id}:CONFIRMED"},
            {"text": "En camino", "callback_data": f"order:{order.id}:ON_THE_WAY"},
        ],
        [
            {"text": "Entregado", "callback_data": f"order:{order.id}:DELIVERED"},
            {"text": "Cancelar", "callback_data": f"order:{order.id}:CANCELLED"},
        ]
    ]

    payload = {
        'chat_id': admin_id,
        'text': text,
        'parse_mode': 'Markdown',
        'reply_markup': {'inline_keyboard': keyboard}
    }

    return send_telegram_with_markup(payload)
