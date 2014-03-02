from misc.tests import TestCase
from django.core.urlresolvers import reverse
from .factories import ParticipationFactory, ParticipantFactory
from main.tests.factories import UserFactory, ConferenceFactory


class ParticipationTest(TestCase):

    params = {
        'first_name': 'Ktoś',
        'last_name': 'Jakiś',
        'phone': '+47123456789',
        'address': 'Gdziesiowo Mniejsze',
    }

    def setUp(self):
        self.user = UserFactory()
        self.client.login(email=self.user.email, password='dummy')

    def test_show(self):
        conference = ConferenceFactory()
        for i in range(10):
            participant = ParticipantFactory(user=self.user)
            ParticipationFactory(participant=participant,
                                 conference=conference)
        url = reverse('participation:show')
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.context['participations']) == 10

    def test_new(self):
        ConferenceFactory()
        url = reverse('participation:new')

        response = self.client.post(url, self.params, follow=True)
        assert response.status_code == 200
        participations = response.context['participations']
        assert len(participations) == 1

        self.check_params(participations[0].participant, self.params)

    def test_edit(self):
        participant = ParticipantFactory(user=self.user)
        participation = ParticipationFactory(participant=participant)
        url = reverse('participation:edit', args=(participation.pk,))

        response = self.client.post(url, self.params, follow=True)
        assert response.status_code == 200

        participant = self.user.participants.get(pk=participant.pk)
        self.check_params(participant, self.params)

    def test_delete(self):
        participant = ParticipantFactory(user=self.user)
        participation = ParticipationFactory(participant=participant)
        url = reverse('participation:delete', args=(participation.pk,))

        response = self.client.post(url, self.params, follow=True)
        assert response.status_code == 200

        assert len(self.user.participants.all()) == 0
