from django import template

register = template.Library()


@register.filter()
def split_by(objs, num):

    it = iter(objs)
    while True:
        tmp = []
        try:
            for _ in range(num):
                tmp.append(next(it))
            yield tmp
        except StopIteration:
            yield tmp
            break
