from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import CustomUserCreationForm
from django.urls import reverse
import logging
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import reverse_lazy

def accounts(request):
    user = request.user
    if user.is_authenticated:
        return redirect("portfolio")
   
    return render(request, "accounts.html")    

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save() 
            logging.info("Uspješna registracija.")
            return redirect(reverse('login'))
        else:
            logging.warning("Neispravan unos prilikom registracije.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            logging.info("Uspješna prijava.")
            return redirect('accounts')
        else:
            logging.warning("Pogreška prilikom prijave.")
            return render(request, 'login.html', {'error': 'Netočno korisničko ime ili lozinka.'})
    return render(request, 'login.html')

def logout(request):
    auth_logout(request)
    logging.info("Odjava uspješna.")
    return redirect('home')

# Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset_form.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    
class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'
    
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    
class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'