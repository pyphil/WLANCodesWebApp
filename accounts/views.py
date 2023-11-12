from django.shortcuts import redirect, render
from django.contrib.auth import login
from .models import RegistrationID
from WLANCodesWebApp.models import Config, AllowedEmail
from .forms import RegisterUserForm, ChangeUsernameForm
from uuid import uuid4
from threading import Thread
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def email_check(request):
    email_error = False
    if request.method == 'POST':
        entered_email = request.POST.get('mail')
        allowed_emails = AllowedEmail.objects.get(school="genm")
        if '@' in entered_email and entered_email.casefold() in allowed_emails.emails.casefold():
            if not User.objects.filter(email=entered_email).exists():
                newuuid = uuid4().hex
                RegistrationID.objects.create(
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
                email_error = "already_used"
        else:
            email_error = "not_allowed"

    return render(request, 'registration/email_check.html', {'email_error': email_error})


def register(request, uuid):
    email_error = False
    link_error = False
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        # check email again just to make sure
        allowed_emails = AllowedEmail.objects.get(school="genm")
        entered_email = request.POST.get('email').casefold()
        if '@' in request.POST.get('email') and entered_email in allowed_emails.emails.casefold():
            if not User.objects.filter(email=entered_email).exists():
                if form.is_valid():
                    form.save()
                    # delete uuid entry
                    u = RegistrationID.objects.get(uuid=uuid)
                    u.delete()
                    return redirect('account_success')
            else:
                email_error = "already_used"
        else:
            email_error = "not_allowed"

    else:
        form = RegisterUserForm()

    # check if user email is authorized
    try:
        u = RegistrationID.objects.get(uuid=uuid)
        user_email = u.user_email
    except RegistrationID.DoesNotExist:
        user_email = None
        link_error = True

    return render(request, 'registration/register.html', {
        'form': form,
        'user_email': user_email,
        'link_error': link_error,
        'email_error': email_error
        }
    )


def registration_email(request):
    return render(request, 'registration/registration_email.html', {})


def account_success(request):
    return render(request, 'registration/account_success.html', {})


@login_required
def change_user(request):
    if request.GET.get('success'):
        success = True
    else:
        success = None
    form = ChangeUsernameForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        # user will be logged out automatically, so log user in again:
        login(request, request.user)
        return redirect('/accounts/change_user/?success=True')
    return render(request, 'registration/change_user.html', {'form': form, 'success': success})


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
