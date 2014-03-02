from django import template
from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


register = template.Library()


@register.filter(is_safe=True)
def form_render(form, temp='default'):
    return mark_safe(render_to_string('form/%s.html' % temp, {"form": form}))


@register.filter(is_safe=True)
def attr(field, attrs):
    """Set attributes to field in template Example::
        {{ field|attr:"class: elegant" }}
        {{ field|attr:"class: disabled, disabled: disabled" }}"""

    for attr in attrs.split(","):
        name, value = attr.split(":", 1)
        field.widget[name.strip()] = value.strip()
    return field


@register.filter(is_safe=True)
def can_set_placeholder(f):
    return isinstance(f.field, forms.CharField)


@register.filter(is_safe=True)
def set_placeholder(f, name):
    field = f.field
    if isinstance(field, forms.CharField):
        field.widget.attrs['placeholder'] = name

    return f
