from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_templated_mail(subject_template, body_template, dictionary, *args, **kwargs):
    subject = render_to_string(subject_template, dictionary).strip()
    body = render_to_string(body_template, dictionary)
    message = EmailMessage(subject, body, *args, **kwargs)
    message.send()
