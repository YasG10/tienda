from django.contrib import admin

# Register your models here.
from .models import Category, Product, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_percent', 'stock', 'is_active', 'average_rating', 'total_reviews')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)
    list_editable = ('price', 'discount_percent', 'stock', 'is_active')
    
    def average_rating(self, obj):
        return f"{obj.average_rating} ⭐"
    average_rating.short_description = 'Rating'
    
    def total_reviews(self, obj):
        return obj.total_reviews
    total_reviews.short_description = 'Reseñas'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'title', 'verified_purchase', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'verified_purchase', 'created_at')
    search_fields = ('title', 'comment', 'user__username', 'product__name')
    list_editable = ('is_approved',)
    readonly_fields = ('created_at', 'updated_at', 'helpful_count')
    
    fieldsets = (
        ('Información del Producto', {
            'fields': ('product', 'user', 'verified_purchase')
        }),
        ('Reseña', {
            'fields': ('rating', 'title', 'comment', 'image')
        }),
        ('Moderación', {
            'fields': ('is_approved', 'helpful_count')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
