from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.conf import settings


def send_mail_service(subject, html_template, recipient_list, context=None):
    plain_message = render_to_string(html_template, context)
    message = strip_tags(plain_message)
    from_email = settings.EMAIL_HOST_USER

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        html_message=plain_message
    )
