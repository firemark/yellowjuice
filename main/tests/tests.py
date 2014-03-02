from django.test import TestCase
from ..models import Conference
from datetime import datetime, timedelta


class ConferenceTest(TestCase):

    def test_range(self):
        start = datetime(year=2012, month=1, day=1, hour=3)
        delta = timedelta(hours=1)
        end = start + delta * 3

        test_list = [start, start + delta, start + delta * 2]

        conf = Conference(start=start, end=end)

        assert test_list == list(conf.datetime_range(delta))
