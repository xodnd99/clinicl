from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Patient

def login_signup_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'register':
            email = request.POST.get('email')
            iin = request.POST.get('iin')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')

            if Patient.objects.filter(email=email).exists():
                messages.error(request, 'Email is already in use')
            elif Patient.objects.filter(iin=iin).exists():
                messages.error(request, 'IIN is already in use')
            else:
                user = Patient.objects.create_user(email=email, iin=iin, password=password, first_name=first_name, last_name=last_name)
                messages.success(request, 'Registration successful. Please log in.')
            return redirect(reverse('login-signup') + '?tab=login')

        elif action == 'login':
            iin = request.POST.get('iin')
            password = request.POST.get('password')
            user = authenticate(request, username=iin, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Вход успешно выполнен!')
            else:
                messages.error(request, 'Invalid IIN or password')
                return redirect(reverse('login-signup') + '?tab=login')

    return render(request, 'registration/login.html', {
        'tab': 'signup' if request.GET.get('tab') == 'signup' else 'login'
    })

