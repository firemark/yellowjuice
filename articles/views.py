from .models import PublishedTranslation
from django.shortcuts import render, get_object_or_404


def show(request, pk, slug):
    """Show Article as one site"""
    translation = get_object_or_404(
        PublishedTranslation,
        draft__article__pk=pk,
        draft__article__visible=True,
        draft__lang__code=request.LANGUAGE_CODE)

    return render(request, 'article/show.html',
                  {"translation": translation})
