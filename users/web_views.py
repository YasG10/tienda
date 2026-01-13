from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from orders.models import Order
from .forms import ProfileForm
from django.contrib import messages


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('catalog:home')
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    # show basic user info and recent orders
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:10]
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            # Debug: confirm file received and saved
            if 'avatar' in request.FILES:
                uploaded = request.FILES['avatar']
                messages.success(request, f'Avatar subido: {uploaded.name}')
            else:
                messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('users:profile')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'users/profile.html', {'recent_orders': recent_orders, 'form': form})
