import factory

from agendas.models import Prelection

from main.tests.factories import ConferenceFactory
from participation.tests.factories import ParticipantFactory
from django.contrib.webdesign.lorem_ipsum import paragraph, words


class PrelectionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Prelection

    main_prelector = factory.SubFactory(ParticipantFactory)
    conference = factory.SubFactory(ConferenceFactory)
    title = factory.LazyAttribute(lambda o: words(5, False)[:50])
    description = factory.LazyAttribute(lambda o: paragraph())
    length = 60

    @factory.post_generation
    def other_prelectors(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for prelector in extracted:
                self.other_prelectors.add(prelector)
