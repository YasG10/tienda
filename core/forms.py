from django import forms
from .models import NewsletterSignup


class NewsletterSignupForm(forms.ModelForm):
    class Meta:
        model = NewsletterSignup
        fields = ('email',)
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'tg-field', 'placeholder': 'you@example.com'}),
        }
