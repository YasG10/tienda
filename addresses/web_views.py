from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import AddressForm

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
            return redirect('addresses:list')
    else:
        form = AddressForm()
    return render(request, 'addresses/create.html', {'form': form})
