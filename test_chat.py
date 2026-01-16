import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from chat.views import my_conversations

User = get_user_model()
user = User.objects.first()

if user:
    rf = RequestFactory()
    req = rf.get('/chat/')
    req.user = user
    
    try:
        resp = my_conversations(req)
        print(f'Success: {resp.status_code}')
    except Exception as e:
        print(f'Error: {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()
else:
    print('No users found')
