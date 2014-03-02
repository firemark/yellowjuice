from django.test import TestCase as DjangoTestCase

class TestCase(DjangoTestCase):

    def check_params(self, obj, params):
        """Check params"""
        for attr, value in params.items():
            assert str(getattr(obj, attr)) == value

