from datetime import datetime, date, timedelta
import factory

from main.models import User, Conference, Currency


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User

    date_joined = factory.LazyAttribute(lambda s: datetime.now())
    email = factory.Sequence(lambda n: "email_%d@foo.com" % n)
    is_active = True

    @factory.post_generation
    def raw_password(self, created, extracted, **kwargs):
        password = extracted if extracted is not None else 'dummy'
        self.set_password(password)
        self.raw_password = password


class ConferenceFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Conference

    start = factory.LazyAttribute(lambda s: date.today() + timedelta(days=365))
    end = factory.LazyAttribute(lambda s: s.start + timedelta(days=3))


class CurrencyFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Currency
