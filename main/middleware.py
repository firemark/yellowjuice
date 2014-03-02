from .models import Conference
from django.core.exceptions import PermissionDenied


class ConferenceMiddleware(object):

    def process_request(self, request):

        if not request.path_info.startswith('/admin/'):
            try:
                request.conference = Conference.get_current()
            except Conference.DoesNotExist:
                raise PermissionDenied
