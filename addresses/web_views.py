from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import AddressForm
from .models import Address

@login_required
def address_list(request):
    addresses = request.user.addresses.all()
    return render(request, 'addresses/list.html', {'addresses': addresses})

@login_required
def address_create(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            addr = form.save(commit=False)
            addr.user = request.user
            # If user sets is_default, unset others
            if addr.is_default:
                request.user.addresses.update(is_default=False)
            addr.save()
            messages.success(request, 'Dirección agregada exitosamente.')
            return redirect('addresses:list')
    else:
        form = AddressForm()
    return render(request, 'addresses/create.html', {'form': form})

@login_required
def set_default_address(request, pk):
    if request.method == 'POST':
        address = get_object_or_404(Address, id=pk, user=request.user)
        # Unset all defaults, then set this one
        request.user.addresses.update(is_default=False)
        address.is_default = True
        address.save()
        messages.success(request, f'Dirección principal actualizada.')
    return redirect('addresses:list')

@login_required
def delete_address(request, pk):
    if request.method == 'POST':
        address = get_object_or_404(Address, id=pk, user=request.user)
        address.delete()
        messages.success(request, 'Dirección eliminada.')
    return redirect('addresses:list')
