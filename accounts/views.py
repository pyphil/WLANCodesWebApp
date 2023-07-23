from django.shortcuts import redirect, render
from .models import Profile
from WLANCodesWebApp.models import Config, AllowedEmail
from .forms import RegisterUserForm
from uuid import uuid4
from django.contrib.auth.models import User
from threading import Thread
from django.core.mail import send_mail


def email_check(request):
    email_error = False
    if request.method == 'POST':
        entered_email = request.POST.get('mail')
        allowed_emails = AllowedEmail.objects.get(school="genm")
        if '@' in entered_email and entered_email.casefold() in allowed_emails.emails.casefold():
            newuuid = uuid4().hex
            Profile.objects.create(
                user_email=entered_email,
                uuid=newuuid,
            )
            # send mail with link in thread
            link = 'https://' + request.get_host() + redirect('register', newuuid).url
            thread = mail_thread(entered_email, link)
            thread.start()
            # render info page about email with registration link
            return redirect('registration_email')
        else:
            email_error = True

    return render(request, 'registration/email_check.html', {'email_error': email_error})


def register(request, uuid):
    email_error = False
    link_error = False
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        allowed_emails = AllowedEmail.objects.get(school="genm")
        if request.POST.get('email') in allowed_emails.emails:
            if form.is_valid():
                form.save()
                return redirect('account_success')
        else:
            email_error = True

    else:
        form = RegisterUserForm()
    
    # check if user email is authorized
    try:
        u = Profile.objects.get(uuid=uuid)
        user_email = u.user_email
    except Profile.DoesNotExist:
        link_error = True

    return render(request, 'registration/register.html', {
        'form': form,
        'user_email': user_email, 
        'link_error': link_error,
        'email_error': email_error})


def registration_email(request):
    return render(request, 'registration/registration_email.html', {})


def account_success(request):
    return render(request, 'registration/account_success.html', {})


def confirm_email(request, uuid):
    # set user active:
    error = False
    try:
        u = User.objects.get(profile__uuid=uuid)
        u.is_active = True
        u.save()
    except User.DoesNotExist:
        error = True

    return render(request, 'registration/email_success.html', {'error': error})


class mail_thread(Thread):
    def __init__(self, email, link):
        super(mail_thread, self).__init__()
        self.link = link
        self.email = email
        conf_mail = Config.objects.get(name="accounts_mail_text")
        conf_noreply = Config.objects.get(name="noreply-mail")
        self.noreply = conf_noreply.setting
        self.mail_text = conf_mail.text

    # run method is automatically executed on thread.start()
    def run(self):
        # send mail
        mail_text = self.mail_text.replace('#LINK#', self.link)

        send_mail(
            'Registrierung WLAN-CodesWebApp',
            mail_text,
            self.noreply,
            [self.email],
            fail_silently=True,
        )
