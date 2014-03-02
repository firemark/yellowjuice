from django.utils import translation
from django.conf import settings


class LanguageMiddleware(object):

    """Change language only for main site - admin must be eng"""

    def process_request(self, request):

        if request.path_info.startswith('/admin/'):
            code = 'eng'
        else:
            code = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME,
                                       settings.LANGUAGE_CODE)

        translation.activate(code)
        request.LANGUAGE_CODE = code

    def process_response(self, request, response):
        translation.deactivate()
        return response
