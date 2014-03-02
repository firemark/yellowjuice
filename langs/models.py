from django.db import models
from django.contrib.admin import site as admin_site


class Language(models.Model):
    """
    Language model
    """
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=6, db_column='shortcut')
    visible = models.BooleanField(default=True)

    def __str__(self):
        return "%s - %s" % (self.code, self.name)

admin_site.register(Language)
