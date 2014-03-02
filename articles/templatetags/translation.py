from django import template
from ..models import PublishedTranslation
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

register = template.Library()


def publish_btn(pk, s, clas='btn-mini'):
    btn = '<a href="%s" class="btn btn-inverse %s">%s</a>'
    return btn % (reverse('admin:publish-translation', args=[pk]), clas, s)


def label(a, b):
    return "<span class='label label-%s'>%s</span> " % (b, a)


def base_status(obj, publish, update, published_str):
    try:
        obj.published
    except PublishedTranslation.DoesNotExist:
        return publish(obj.pk)
    else:
        diff = obj.diff()

        if diff:
            return update(', '.join(diff), obj.pk)
        else:
            return published_str


def status_on_list(obj, has_perm=True):
    """Show status on translations list"""
    published_str = label('published', 'success')

    if has_perm:
        publish = lambda pk: label('draft', 'info') + \
            publish_btn(pk, 'publish')
        update = lambda msg, pk: label('changed (%s)' % msg, 'warning') + \
            publish_btn(pk, 'update')
    else:
        publish = lambda pk: label('draft', 'info')
        update = lambda msg, pk: label('changed (%s)' % msg, 'warning')

    return base_status(obj, publish, update, published_str)


def status_only_button(obj, has_perm=True):
    """Show only button to publish"""
    publish = lambda pk: publish_btn(pk, 'Publish', '')
    update = lambda msg, pk: publish_btn(pk, 'Update', '')
    published_str = '<button class="btn btn-inverse" disabled>%s</button>'

    return base_status(obj, publish, update, published_str % 'Published')


@register.filter(name='status', is_safe=True)
def safe_status_with_perm(obj, where=''):
    if where != 'button':
        return mark_safe(status_on_list(obj, True))
    else:
        return mark_safe(status_only_button(obj, True))


@register.filter(name='status_without_perms', is_safe=True)
def safe_status_without_perms(obj, where=''):
    if where != 'button':
        return mark_safe(status_on_list(obj, False))
    else:
        return mark_safe(status_only_button(obj, False))
