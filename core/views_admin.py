from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from catalog.models import Product, Category
from orders.models import Order, OrderItem
from users.models import User
from django.db.models import Sum, Count, Q, F, Avg
from django.utils import timezone
from datetime import timedelta
import json

@staff_member_required
def admin_dashboard(request):
    # Contadores generales
    productos = Product.objects.count()
    productos_activos = Product.objects.filter(is_active=True).count()
    categorias = Category.objects.count()
    pedidos = Order.objects.count()
    usuarios = User.objects.filter(role='CLIENT').count()
    
    # Ingresos
    ingresos_totales = Order.objects.exclude(
        status=Order.STATUS_CANCELLED
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Ingresos del mes actual
    hoy = timezone.now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ingresos_mes = Order.objects.filter(
        created_at__gte=inicio_mes
    ).exclude(
        status=Order.STATUS_CANCELLED
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Ingresos de la semana
    inicio_semana = hoy - timedelta(days=7)
    ingresos_semana = Order.objects.filter(
        created_at__gte=inicio_semana
    ).exclude(
        status=Order.STATUS_CANCELLED
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Pedidos por estado
    pedidos_pendientes = Order.objects.filter(status=Order.STATUS_PENDING).count()
    pedidos_confirmados = Order.objects.filter(status=Order.STATUS_CONFIRMED).count()
    pedidos_enviados = Order.objects.filter(status=Order.STATUS_ON_THE_WAY).count()
    pedidos_entregados = Order.objects.filter(status=Order.STATUS_DELIVERED).count()
    pedidos_cancelados = Order.objects.filter(status=Order.STATUS_CANCELLED).count()
    
    # Stock crítico (productos con stock <= 5)
    productos_sin_stock = Product.objects.filter(stock=0, is_active=True).count()
    productos_stock_bajo = Product.objects.filter(stock__lte=5, stock__gt=0, is_active=True).count()
    
    # Pedidos recientes
    pedidos_recientes = Order.objects.select_related('user', 'address').order_by('-created_at')[:10]
    
    # Productos más vendidos
    productos_mas_vendidos = OrderItem.objects.values(
        'product__name', 'product__id'
    ).annotate(
        total_vendido=Sum('quantity')
    ).order_by('-total_vendido')[:5]
    
    # Usuarios recientes
    usuarios_recientes = User.objects.filter(
        role='CLIENT'
    ).order_by('-date_joined')[:5]
    
    # Productos con stock bajo
    productos_stock_critico = Product.objects.filter(
        Q(stock=0) | Q(stock__lte=5),
        is_active=True
    ).order_by('stock')[:10]
    
    # Ventas de los últimos 7 días (para gráfico)
    ventas_semana = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        inicio_dia = dia.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = inicio_dia + timedelta(days=1)
        ventas_dia = Order.objects.filter(
            created_at__gte=inicio_dia,
            created_at__lt=fin_dia
        ).exclude(
            status=Order.STATUS_CANCELLED
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        ventas_semana.append({
            'dia': dia.strftime('%d/%m'),
            'total': float(ventas_dia)
        })
    
    # Pedidos de los últimos 7 días (para gráfico)
    pedidos_semana = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        inicio_dia = dia.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = inicio_dia + timedelta(days=1)
        count = Order.objects.filter(
            created_at__gte=inicio_dia,
            created_at__lt=fin_dia
        ).count()
        pedidos_semana.append({
            'dia': dia.strftime('%d/%m'),
            'count': count
        })
    
    # Ticket promedio
    ticket_promedio = Order.objects.exclude(
        status=Order.STATUS_CANCELLED
    ).aggregate(promedio=Avg('total_amount'))['promedio'] or 0
    
    context = {
        'productos': productos,
        'productos_activos': productos_activos,
        'categorias': categorias,
        'pedidos': pedidos,
        'usuarios': usuarios,
        'ingresos_totales': round(ingresos_totales, 2),
        'ingresos_mes': round(ingresos_mes, 2),
        'ingresos_semana': round(ingresos_semana, 2),
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_confirmados': pedidos_confirmados,
        'pedidos_enviados': pedidos_enviados,
        'pedidos_entregados': pedidos_entregados,
        'pedidos_cancelados': pedidos_cancelados,
        'productos_sin_stock': productos_sin_stock,
        'productos_stock_bajo': productos_stock_bajo,
        'pedidos_recientes': pedidos_recientes,
        'productos_mas_vendidos': productos_mas_vendidos,
        'usuarios_recientes': usuarios_recientes,
        'productos_stock_critico': productos_stock_critico,
        'ventas_semana_json': json.dumps(ventas_semana),
        'pedidos_semana_json': json.dumps(pedidos_semana),
        'ticket_promedio': round(ticket_promedio, 2),
    }
    
    return render(request, 'admin_dashboard.html', context)
