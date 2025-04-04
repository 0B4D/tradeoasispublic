from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import CustomUserCreationForm
from django.urls import reverse
import logging
from django.urls import reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)


def accounts(request):
    user = request.user
    if user.is_authenticated:
        return redirect("portfolio")
   
    return render(request, "accounts.html")    

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Don't save the user immediately - set commit=False
            user = form.save(commit=False)
            # Set user to inactive until email is confirmed
            user.is_active = False
            user.save()
            
            # Generate confirmation link
            current_site = get_current_site(request)
            mail_subject = 'Aktivirajte svoj račun'
            message = render_to_string('account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            
            # Send email
            email = EmailMessage(
                mail_subject, 
                message, 
                to=[user.email]
            )
            email.send()
            
            logging.info(f"Uspješna registracija korisnika {user.username}. Poslana email potvrda.")
            return render(request, 'register_done.html', {'email': user.email})
        else:
            logging.warning("Neispravan unos prilikom registracije.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Vaš račun je uspješno aktiviran! Možete se prijaviti.')
        logging.info(f"Uspješna aktivacija računa za korisnika {user.username}.")
        return redirect('login')
    else:
        messages.error(request, 'Link za aktivaciju nije valjan ili je istekao!')
        logging.warning(f"Neuspjela aktivacija računa.")
        return redirect('login')

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