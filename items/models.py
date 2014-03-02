from django.db import models
from participation.models import Participation


class OptionGroup(models.Model):
    key = models.CharField(max_length=70)
    visible = models.BooleanField(default=True)
    show_description = models.BooleanField(default=False)
    required = models.BooleanField(default=False)

    def __str__(self):
        return self.key


class OptionItem(models.Model):
    key = models.CharField(max_length=70)
    group = models.ForeignKey(OptionGroup, related_name='options')
    visible = models.BooleanField(default=True)

    def __str__(self):
        return '{}(group: {})'.format(self.key, self.group)


class OptionCurrency(models.Model):
    option = models.ForeignKey(OptionItem, related_name='currencies')
    price = models.DecimalField(max_digits=7, decimal_places=2)
    currency = models.ForeignKey('main.Currency',
                                 related_name='option_currencies')

    class Meta:
        unique_together = ['option', 'currency']

    def __str__(self):
        return str(self.currency)


class OptionTranslate(models.Model):
    option = models.ForeignKey(OptionItem, related_name='translates')
    lang = models.ForeignKey("langs.Language")
    name = models.CharField(max_length=70)

    class Meta:
        unique_together = ['option', 'lang']

    def __str__(self):
        return str(self.lang)


class OptionGroupTranslate(models.Model):
    group = models.ForeignKey(OptionGroup, related_name='translates')
    lang = models.ForeignKey("langs.Language")
    name = models.CharField(max_length=70)
    description = models.TextField()

    class Meta:
        unique_together = ['group', 'lang']

    def __str__(self):
        return str(self.lang)


class Option(models.Model):

    ''' Participation Option chosen by Participant '''
    participation = models.ForeignKey(Participation, related_name='options')
    option_item = models.ForeignKey(OptionItem)

    def __str__(self):
        return '{option!s} {participation!s}'.format(
            option=self.option_item, participation=self.participation
        )

    class Meta:
        unique_together = ['participation', 'option_item']

__all__ = [name for name in locals() if name.startswith("Option")]
