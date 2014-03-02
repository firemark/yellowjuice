from django.utils.translation import activate
from .models import Language
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.conf import settings


def change_language(request, code):
    get_object_or_404(Language, code=code, visible=True)
    activate(code)

    response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, code)

    return response
