from django.http import JsonResponse
from django.views.decorators.http import require_GET

def keep_alive(request):
    return JsonResponse({'status': 'ok', 'message': 'alive'})
