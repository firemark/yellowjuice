from django.test import TestCase
from ..models import Article, DraftTranslation, PublishedTranslation
from main.tests.factories import UserFactory
from .factories import ArticleFactory, TranslationFactory
from langs.models import Language
from main.models import User
from django.db.models import F


class TranslationTest(TestCase):

    def setUp(self):
        langs = (
            ('polish', 'pl'),
            ('english', 'eng')
        )
        for name, code in langs:
            Language.objects.create(name=name, code=code)

        UserFactory(email='translator@b.pl')
        UserFactory(email='user@a.pl')
        ArticleFactory()

    def test_relations(self):
        article = Article.objects.get(pk=1)
        translator = User.objects.get(email='translator@b.pl')

        lang_pl = Language.objects.get(code='pl')
        lang_eng = Language.objects.get(code='eng')

        TranslationFactory(author=translator, article=article, lang=lang_pl)

        assert DraftTranslation.objects.filter(article=article).count() == 1
        assert DraftTranslation.objects.filter(
            article=article,
            lang=lang_pl).count() == 1
        assert DraftTranslation.objects.filter(
            article=article,
            lang=lang_eng).count() == 0
        assert DraftTranslation.objects.filter(author=translator).count() == 1
        assert DraftTranslation.objects.filter(
            author__email='user@a.pl'
        ).count() == 0

    def test_published(self):
        article = Article.objects.get(pk=1)
        translator = User.objects.get(email='translator@b.pl')
        lang_pl = Language.objects.get(code='pl')

        translation = TranslationFactory(author=translator,
                                         article=article,
                                         lang=lang_pl)

        published = translation.publish()
        manager = PublishedTranslation.objects
        assert manager.filter(pk=published.pk).count() == 1
        assert manager.filter(draft=translation).count() == 1
        assert manager.filter(draft__article=article).count() == 1
        assert manager.filter(text=F('draft__text'),
                              slug=F('draft__slug'),
                              title=F('draft__title')).count() == 1
