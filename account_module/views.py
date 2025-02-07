from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.utils.translation.trans_null import gettext_lazy as _
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView

from utils.mail_service import send_mail_service
from .forms import RegisterForm, LoginForm
from .models import Account
from uuid import uuid4

# Create your views here.


class RegisterView(FormView):
    template_name = "account_module/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("index-page")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("شما به این صفحه دسترسی ندارید.")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # entered user detail
        entered_first_name = form.cleaned_data.get("first_name")
        entered_last_name = form.cleaned_data.get("last_name")
        entered_username = form.cleaned_data.get("username")
        entered_email = form.cleaned_data.get("email")
        entered_password = form.cleaned_data.get("password1")
        entered_phone_number = form.cleaned_data.get("phone_number")

        # check user details are unique
        is_phone_number_unique = Account.objects.filter(phone_number=entered_phone_number).exists()
        is_email_unique = Account.objects.filter(email=entered_email).exists()

        if not is_phone_number_unique:
            if not is_email_unique:

                # create the new user and save it to db
                user: Account = Account(
                    first_name=entered_first_name,
                    last_name=entered_last_name,
                    username=entered_username,
                    email=entered_email,
                    phone_number=entered_phone_number,
                    is_active=False,
                )

                user.set_password(entered_password)
                user.save()

                # Send activation email to user
                email_context = {"active-code": user.active_code}
                send_mail_service(
                    "فعال سازی حساب کاربری",
                    "emails/activation-email.html",
                    list(user.email),
                    email_context
                )

            else:
                form.add_error("email",  _("کابری با این ایمیل وجود دارد."))
        else:
            form.add_error("phone_number", _("کاربری با این شماره تلفن وجود دارد."))
        return super().form_valid(form)


class LoginView(LoginView):
    template_name = "account_module/login.html"
    redirect_authenticated_user = True
    next_page = reverse_lazy("index-page")
    authentication_form = LoginForm


def activation_view(request, active_code):
    if not request.user.is_authenticated:
        user: Account = Account.objects.get(active_code=active_code)

        if user is not None and user.is_active:
            user.is_active = True
            user.active_code = uuid4()
            user.save()

            return redirect(reverse("index-page"))

        return redirect(reverse("index-page"))

    return HttpResponseForbidden(_("شما به این صفحه دسترسی ندارید."))


@login_required
def logout_view(request):
    logout(request)
    
    return render(request, "account_module/logout.html")
