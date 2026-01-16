from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Formulario para crear/editar reseñas"""
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment', 'image']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} ⭐') for i in range(1, 6)]),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Resumen de tu experiencia'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 5,
                'placeholder': 'Comparte tu experiencia con este producto...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100',
                'accept': 'image/*'
            }),
        }
        labels = {
            'rating': 'Tu calificación',
            'title': 'Título de tu reseña',
            'comment': 'Tu opinión',
            'image': 'Foto (opcional)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS personalizadas al campo rating
        self.fields['rating'].widget.attrs.update({
            'class': 'rating-stars'
        })
