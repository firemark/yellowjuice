from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.conf import settings
from .settings import TIMEDELTA


class UserManager(BaseUserManager):

    def create_user(self, username=None, email=None, password=None):
        user = self.model(email=self.normalize_email(username or email))
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username=None, email=None, password=None):
        user = self.create_user(username or email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser):

    """Custom user model"""
    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['email']

    objects = UserManager()

    email = models.EmailField(unique=True)
    last_conference = models.ForeignKey("Conference", blank=True, null=True)

    # site_lang = models.ForeignKey('cms.Language')
    is_administrator = models.BooleanField(default=False)
    is_organizator = models.BooleanField(default=False)
    is_reviewer = models.BooleanField(default=False)
    is_translator = models.BooleanField(default=False)

    # Those fields are here to make syncdb's admin creation work
    # (probably some other things in Django aassume they exist, too)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    currency = models.ForeignKey("main.Currency", blank=True, null=True)

    def get_full_name(self):
        """Return long user's name"""
        if hasattr(self, 'participant'):
            return '{p.first_name} {p.last_name}'.format(p=self.participant)
        else:
            return self.email

    def get_short_name(self):
        """Return short name"""
        return self.participant.first_name if hasattr(self, 'participant') \
            else self.email

    def has_perm(self, perm, obj=None):
        if self.is_superuser:
            return True
        perm = perm.split('.')[0]  # app_name.perm
        try:
            perms = settings.MODULE_PERMS[perm]
        except KeyError:
            return getattr(self, 'is_%s' % perm, False)
        else:
            for perm in perms:
                if getattr(self, 'is_%s' % perm, False):
                    return True
            return False

    def has_module_perms(self, app_label):
        return True


class UserConfirm(models.Model):
    user = models.ForeignKey(User)
    key = models.CharField(max_length=32)


class Conference(models.Model):
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)

    open_for_prelection = models.BooleanField(default=False)
    open_register = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    @classmethod
    def get_current(cls):
        """Return the oncomming/current conference"""
        return cls.objects.filter(is_active=True).get()

    def save(self, *args, **kwargs):
        if self.is_active:
            # only one may has is_active flag
            Conference.objects.filter(is_active=True).update(is_active=False)

        super().save(*args, **kwargs)

    def __str__(self):
        if self.start is not None:
            return "start %s" % self.start.strftime("%Y-%d")
        else:
            return "in the future"

    def agenda(self):
        return self.prelections.filter(time__isnull=False).order_by('time')

    def not_added_prelections(self):
        return self.prelections.filter(time__isnull=True).order_by('title')

    def datetime_range(self, delta=timedelta(minutes=TIMEDELTA)):
        dt = self.start

        while dt < self.end:
            yield dt
            dt += delta


class Currency(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=3)

    def __str__(self):
        return '{:s} ({:s})'.format(self.code, self.name)
