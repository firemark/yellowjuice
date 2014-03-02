from django.core.mail import send_mail as django_send_email
from django.template.loader import get_template
from django.template import Context


def send_email(topic, template_path, context_dict, emails):
    context = Context(context_dict)
    render = get_template(template_path).render(context)

    django_send_email(topic, render, "noreply@sok.com", emails)
