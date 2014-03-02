from django.core.management.base import BaseCommand
from main.tests.factories import (UserFactory, ConferenceFactory,
                                  CurrencyFactory)
from participation.tests.factories import (ParticipationFactory,
                                           ParticipantFactory)
from articles.tests.factories import ArticleFactory, TranslationFactory
from items.tests.factories import OptionGroupFactory, OptionItemFactory
from articles.models import Menu
from agendas.tests.factories import PrelectionFactory
from random import randint, choice
from langs.models import Language
from main.models import Currency
from sys import stdout
from datetime import datetime


class Command(BaseCommand):

    """every app in tuple calls create_APPNAME method"""

    apps = (
        'users',
        'conference',
        'currencies',
        'languages',
        'articles',
        'participants',
        'prelections',
        'options',
        # todo payments
    )

    def create_users(self):
        UserFactory(email='admin@foo.com',
                    raw_password='foobar',
                    is_administrator=True,
                    is_superuser=True,
                    is_staff=True)

    def create_languages(self):
        Language.objects.create(name='Polski', code='pl_PL')
        Language.objects.create(name='English', code='en_US')

    def create_articles(self):
        titles = ['About', 'News', 'Program', 'Speakers', 'Sponsors']
        langs = list(Language.objects.all())

        for i, title in enumerate(titles):
            translator = UserFactory(raw_password='foobar',
                                     is_translator=True,
                                     is_staff=True)
            article = ArticleFactory(author=translator)
            Menu.objects.create(article=article, position=i)

            for lang in langs:
                TranslationFactory(article=article,
                                   lang=lang,
                                   author=translator,
                                   title=title,
                                   published=True)

    def create_participants(self):
        num = randint(5, 10)
        conf = self.conference
        [ParticipationFactory(conference=conf) for i in range(num)]

    def create_prelections(self):
        num = randint(2, 5)

        conf = self.conference
        for i in range(num):
            user = UserFactory()
            prelectors_num = choice([1, 1, 1, 1, 2, 2, 3])  # probability
            main_prelector, *other_prelectors = [
                ParticipationFactory(
                    participant=ParticipantFactory(user=user),
                    conference=conf
                ).participant
                for _ in range(prelectors_num)
            ]

            PrelectionFactory(conference=conf,
                              main_prelector=main_prelector,
                              other_prelectors=other_prelectors)

    def create_options(self):
        group_num = randint(2, 5)

        langs = list(Language.objects.all())
        currencies = list(Currency.objects.all())
        for i in range(group_num):
            items_num = randint(2, 5)
            group = OptionGroupFactory(langs=langs)
            group_key = group.key
            for j in range(items_num):
                OptionItemFactory(langs=langs,
                                  key="{} {}".format(group_key, "★" * j),
                                  group=group,
                                  currencies=currencies)

    def create_currencies(self):
        CurrencyFactory(name=u"Złoty", code="PLN")
        CurrencyFactory(name=u"Dollars", code="USD")

    def create_conference(self):
        self.conference = ConferenceFactory(open_for_prelection=True)

    def handle(self, *args, **kwargs):
        stdout.write("\033[95m")
        stdout.write("Create test data".center(79, '-'))
        stdout.write("\033[0m\n\n")

        total_start = datetime.now()

        for app in self.apps:
            stdout.write("Create %s... " % app.replace('_', ' ').capitalize())
            stdout.flush()
            start = datetime.now()
            function = getattr(self, 'create_%s' % app)
            function()
            end = datetime.now()

            diff = (end - start).total_seconds()
            stdout.write("time: %.2f seconds\n" % diff)

        total_end = datetime.now()

        diff = (total_end - total_start).total_seconds()
        stdout.write("Total time: %.2f seconds\n" % diff)
