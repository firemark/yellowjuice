from ..models import (OptionItem, OptionGroup, OptionTranslate,
                      OptionGroupTranslate, OptionCurrency)
from django.contrib.webdesign.lorem_ipsum import words
from random import randint
from decimal import Decimal
import factory


def langs_gen(cls):
    def langs(self, create, extracted, **kwargs):

        if not extracted:
            return

        key = self.key

        for lang in extracted:
            self.translates.add(cls(
                lang=lang,
                name="{}-{}".format(lang.code, key)
            ))

    return factory.post_generation(langs)


class OptionGroupFactory(factory.DjangoModelFactory):
    FACTORY_FOR = OptionGroup

    key = factory.Sequence(lambda n: "GROUP %d" % n)
    langs = langs_gen(OptionGroupTranslate)

    @factory.post_generation
    def items(self, create, extracted, **kwargs):

        if not extracted:
            return

        if randint(0, 5) >= 3:
            self.show_description = True

        if randint(0, 5) >= 3:
            self.required = True

        for item in extracted:
            if self.show_description:
                item.description = '\r\n\r\n  '.join(words(randint(2, 7), True))
            self.translates.add(item)


class OptionItemFactory(factory.DjangoModelFactory):
    FACTORY_FOR = OptionItem

    group = factory.SubFactory(OptionGroupFactory)
    key = factory.Sequence(lambda n: "ITEM %d" % n)
    langs = langs_gen(OptionTranslate)

    @factory.post_generation
    def currencies(self, create, extracted, **kwargs):
        if not extracted:
            return

        for currency in extracted:
            self.currencies.add(OptionCurrency(
                currency=currency,
                price=Decimal(randint(1000, 10000)) / 100
            ))
