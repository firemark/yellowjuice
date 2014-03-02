import factory
import factory.fuzzy
from participation.models import Participant, Participation
from main.tests.factories import UserFactory, ConferenceFactory

first_names = ('Harry', 'Oliver', 'Jack', 'Charlie', 'Jacob', 'Thomas',
               'Alfie', 'Riley', 'William', 'James', 'Amelia', 'Olivia',
               'Jessica', 'Emily', 'Lily', 'Ava', 'Isla', 'Sophie', 'Mia'
               'Isabella')
last_names = ('Brown', 'Smith', 'Patel', 'Jones', 'Williams', 'Smith',
              'Patel', 'Jones', 'Williams', 'Johnson', 'Taylor', 'Thomas',
              'Roberts', 'Khan', 'Smith', 'Patel', 'Jones', 'Williams',
              'Johnson', 'Taylor', 'Thomas', 'Roberts', 'Khan', 'Lewis')


class ParticipantFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Participant

    user = factory.SubFactory(UserFactory)
    first_name = factory.fuzzy.FuzzyChoice(first_names)
    last_name = factory.fuzzy.FuzzyChoice(last_names)
    # adress generator? ideas?


class ParticipationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Participation

    participant = factory.SubFactory(ParticipantFactory)
    conference = factory.SubFactory(ConferenceFactory)
