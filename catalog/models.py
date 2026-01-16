from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    
    # Al configurar STORAGES en settings, este campo
    # automáticamente subirá a Cloudinary
    image = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True
    )
    
    discount_percent = models.PositiveIntegerField(default=0, help_text="Descuento en porcentaje (0-100)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.stock})"

    @property
    def is_available(self):
        return self.is_active and self.stock > 0

    @property
    def price_with_discount(self):
        if self.discount_percent:
            # Convertimos a float para el cálculo, aunque idealmente se usa Decimal para dinero
            return round(float(self.price) * (1 - self.discount_percent / 100), 2)
        return float(self.price)
    
    @property
    def average_rating(self):
        """Calcula el rating promedio del producto"""
        avg = self.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0
    
    @property
    def total_reviews(self):
        """Cuenta total de reseñas aprobadas"""
        return self.reviews.filter(is_approved=True).count()
    
    @property
    def rating_distribution(self):
        """Distribución de calificaciones por estrellas"""
        distribution = {i: 0 for i in range(1, 6)}
        reviews = self.reviews.filter(is_approved=True)
        total = reviews.count()
        
        if total == 0:
            return distribution
        
        for i in range(1, 6):
            count = reviews.filter(rating=i).count()
            distribution[i] = {
                'count': count,
                'percentage': round((count / total) * 100, 1)
            }
        return distribution


class Review(models.Model):
    """Modelo para reseñas de productos"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación de 1 a 5 estrellas"
    )
    title = models.CharField(
        max_length=200,
        help_text="Título breve de la reseña"
    )
    comment = models.TextField(
        help_text="Cuéntanos tu experiencia con el producto"
    )
    image = models.ImageField(
        upload_to='reviews/',
        null=True,
        blank=True,
        help_text="Foto opcional del producto"
    )
    is_approved = models.BooleanField(
        default=True,
        help_text="¿La reseña está aprobada para mostrarse?"
    )
    verified_purchase = models.BooleanField(
        default=False,
        help_text="¿El usuario compró este producto?"
    )
    helpful_count = models.PositiveIntegerField(
        default=0,
        help_text="Cantidad de usuarios que encontraron útil esta reseña"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # Un usuario solo puede dejar una reseña por producto
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}★)"