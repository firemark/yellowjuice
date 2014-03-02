from django.conf import settings
from django.db import models


class TypesDict(models.Model):
    name = models.CharField(max_length=70)


class Payment(models.Model):
    class STATUSES(object):
        REQUESTED = 'RQS'
        REGISTERED = 'REG'
        TO_VERIFY = 'TVR'
        ACCEPTED = 'ACP'
        REJECTED = 'RJC'
        CANCELLED = 'CCL'

    STATUS_CHOICES = (
        (STATUSES.REQUESTED, 'Requested.'),
        (STATUSES.REGISTERED, 'Registered.'),
        (STATUSES.TO_VERIFY, 'Waiting for verification.'),
        (STATUSES.ACCEPTED, 'Accepted.'),
        (STATUSES.REJECTED, 'Rejected.'),
        (STATUSES.CANCELLED, 'Cancelled.'),
    )

    sender_user_id = models.ForeignKey(settings.AUTH_USER_MODEL,
                                       editable=False)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    payment_type_id = models.ForeignKey(TypesDict)
    description = models.TextField()
    creation_time = models.DateTimeField()


class Comment(models.Model):
    payment_id = models.ForeignKey(Payment)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False)
    time = models.DateTimeField()
    comment = models.CharField(max_length=200)
