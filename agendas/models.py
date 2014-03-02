from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext as _


class PrelectionQuerySet(models.Manager):

    def can_see(self, user, conference):
        """Return only prelections that `user` can see"""
        return self.filter(
            Q(main_prelector__user=user) | Q(other_prelectors__user=user),
            conference=conference)

    def can_edit(self, user, conference):
        """Can this user edit a prelection?
        Here "edit" means "change description/length", and not status"""
        return self.filter(main_prelector__user=user, conference=conference)

    def can_see_with_req(self, request):
        return self.can_see(request.user, request.conference)

    def can_edit_with_req(self, request):
        return self.can_edit(request.user, request.conference)

    def can_delete_with_req(self, request):
        return self.can_edit(request.user, request.conference)

    def can_create(self, user):
        """Can this user create prelections?"""
        return user.participant_set.exists()

    def can_comment(self, user):
        """Prelections this user can comment"""
        if user.is_reviewer:
            return self
        else:
            return self.filter(pk=-1)

    def owned_by(self, user):
        """Return prelections owned by given user"""
        return self.filter(prelector__user=user)

    def not_added(self):
        """Prelections not yet added to agenda"""
        return self.exclude(status=Prelection.STATUSES.ADDED)


class Room(models.Model):
    key = models.CharField(max_length=50)
    conference = models.ForeignKey('main.Conference', related_name="rooms")


class RoomTranslate(models.Model):
    name = models.CharField(max_length=50)
    lang = models.ForeignKey("langs.Language")
    room = models.ForeignKey(Room)

    class Meta:
        unique_together = ['lang', 'room']


class Prelection(models.Model):

    class STATUSES(object):
        PROPOSED = 'PRP'
        ACCEPTED = 'ACC'
        REJECTED = 'RJC'
        ADDED = 'ADD'

    STATUS_CHOICES = (
        (STATUSES.PROPOSED, _('Proposed')),
        (STATUSES.ACCEPTED, _('Accepted')),
        (STATUSES.REJECTED, _('Rejected')),
        (STATUSES.ADDED, _('Added')),
    )
    conference = models.ForeignKey('main.Conference',
                                   related_name="prelections")
    room = models.ForeignKey(Room,
                             related_name="prelections", null=True, blank=True)

    main_prelector = models.ForeignKey('participation.Participant',
                                       related_name="main_prelections")
    other_prelectors = models.ManyToManyField(
        'participation.Participant',
        related_name="submain_prelections"
    )
    title = models.CharField(max_length=50)
    description = models.TextField()
    status = models.CharField(max_length=3,
                              choices=STATUS_CHOICES,
                              default=STATUSES.PROPOSED)
    length = models.PositiveIntegerField('Length', help_text="in minutes")
    """Stores length in minutes"""
    time = models.DateTimeField(null=True, blank=True)
    """When will this prelection happen (if it's added)"""

    objects = PrelectionQuerySet()

    def accept(self):
        self.status = self.STATUSES.ACCEPTED
        self.time = None
        self.room = None

    def reject(self):
        self.status = self.STATUSES.REJECTED
        self.time = None
        self.room = None

    @property
    def comments(self):
        return self.comments_set.all()

    def get_absolute_url(self):
        return reverse('panel/prelection-update', args=(self.pk, ))


class PrelectionFile(models.Model):
    prelection = models.ForeignKey(Prelection, related_name="prelections")
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to="prelection_files")


class ReviewerComment(models.Model):
    content = models.TextField()
    prelection = models.ForeignKey(Prelection, related_name='comments_set')
    author = models.ForeignKey(settings.AUTH_USER_MODEL)

    def get_absolute_url(self):
        return '{url}#comment-{pk}'.format(
            url=self.prelection.get_absolute_url(),
            pk=self.pk)

    def __repr__(self):
        return '<{type}: {author}@{prelection}: {content}>'.format(
            type=type(self), author=self.author,
            prelection=repr(self.prelection),
            content=repr(self.content[:20]))
