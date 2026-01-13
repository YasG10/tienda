from django.contrib import admin
from .models import Address

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'street', 'phone', 'is_default')
    list_filter = ('city',)
    search_fields = ('street', 'city', 'user__username')
