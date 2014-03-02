from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _


class ParticipantManager(models.Manager):

    def can_see(self, user, conference):
        return self.filter(participations__conference=conference, user=user)

    def can_edit(self, user):
        return self.filter(user=user)

    def can_see_with_req(self, request):
        return self.can_see(request.user, request.conference)

    @staticmethod
    def can_create(user):
        return user.is_authenticated


class ParticipationManager(models.Manager):

    def present_with_req(self, request):
        return self.select_related('participant').\
            filter(conference=request.conference,
                   participant__user=request.user)

    def old_with_req(self, request):
        return self.select_related('participant').\
            filter(participant__user=request.user).\
            exclude(conference=request.conference)


class Participant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             editable=False,
                             related_name='participants')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birthday = models.DateField(null=True)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=200)

    objects = ParticipantManager()

    @property
    def full_name(self):
        return '{!s} {!s}'.format(self.first_name, self.last_name)

    def __str__(self):
        return self.full_name


class Participation(models.Model):

    class STATUSES(object):
        REGISTERED = 'REG'
        CONFIRMED = 'CFR'
        CANCELLED = 'CCL'
        VALID = 'VLD'
        PRESENT = 'PRS'

    STATUS_CHOICES = (
        (STATUSES.REGISTERED, _('Registered')),
        (STATUSES.CONFIRMED, _('Confirmed by participant')),
        (STATUSES.CANCELLED, _('Cancelled')),
        (STATUSES.VALID, _('Valid')),
        (STATUSES.PRESENT, _('Present on a conference')),
    )

    participant = models.ForeignKey(Participant,
                                    editable=False,
                                    related_name='participations')
    conference = models.ForeignKey('main.Conference')
    status = models.CharField(max_length=3,
                              choices=STATUS_CHOICES,
                              default=STATUSES.REGISTERED)

    objects = ParticipationManager()

    def __str__(self):
        return self.participant.full_name
