from .models import Menu


def menu(request):
    menu = (Menu.objects
            .filter(article__visible=True,
                    article__translations__published__isnull=False,
                    article__translations__lang__code=request.LANGUAGE_CODE)
            .order_by('position')
            .select_related('article__translations__published')
            .values('article__translations__published__title',
                    'article__translations__published__slug',
                    'article__pk'))

    # get more clean names
    pretty_menu = [{key.split('__')[-1]: val
                    for key, val in node.items()}
                   for node in menu]

    return {"menu": pretty_menu}
