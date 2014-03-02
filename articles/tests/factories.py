import factory
from articles.models import Article, DraftTranslation
from main.tests.factories import UserFactory
from django.contrib.webdesign.lorem_ipsum import paragraphs, words
from random import randint
import factory.fuzzy


class ArticleFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Article

    author = factory.SubFactory(UserFactory)
    visible = True


class TranslationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DraftTranslation

    # todo: lorem ipsum
    article = factory.SubFactory(ArticleFactory)
    author = factory.SubFactory(UserFactory)
    title = factory.LazyAttribute(lambda o: words(randint(1, 3), False)[:50])
    slug = factory.LazyAttribute(
        lambda o: o.title.replace(' ', '-').lower()[:20]
    )

    @factory.lazy_attribute
    def text(self):
        return '\r\n\r\n  '.join(paragraphs(randint(2, 4), True))

    @factory.post_generation
    def published(self, created, extracted, **kwargs):
        if extracted:
            self.publish()
