from django.conf import settings

TIMEDELTA = getattr(settings, 'TIMEDELTA', 15)  # in minutes
