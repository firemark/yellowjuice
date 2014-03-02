from django.db import models
from django.conf import settings
from langs.models import Language


class Article(models.Model):

    """Article Model
    """
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name="articles_owner")
    visible = models.BooleanField(default=True)

    def __str__(self):
        tran = self.translations.order_by('id').only('title')

        return tran[0].title if tran else 'Untitled'


class DraftTranslation(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name="translations_owner")
    lang = models.ForeignKey(Language, related_name="translations")
    article = models.ForeignKey(Article, related_name="translations")

    slug = models.SlugField(max_length=20)
    title = models.CharField(blank=True, max_length=50)
    text = models.TextField(blank=True)

    posted_date = models.DateTimeField(auto_now_add=True)
    edited_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('article', 'lang')

    def __str__(self):
        return "%s:%s" % (self.lang.code, self.title)

    def publish(self):
        published = PublishedTranslation(
            slug=self.slug,
            title=self.title,
            text=self.text)

        try:
            published.pk = self.published.pk
        except PublishedTranslation.DoesNotExist:
            pass

        published.clean_fields(exclude=['draft'])
        self.published = published
        published.save()
        self.save()

        return published

    def diff(self):
        """Return list of attributes was not changed"""
        published = self.published
        if not published:
            raise PublishedTranslation.DoesNotExist
        return [a for a in ('slug', 'title', 'text')
                if getattr(self, a) != getattr(published, a)]


class PublishedTranslation(models.Model):
    draft = models.OneToOneField(
        DraftTranslation,
        primary_key=True,
        related_name="published")

    slug = models.SlugField(max_length=20)
    title = models.CharField(blank=False, max_length=50)
    text = models.TextField()

    publish_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.draft)


class Menu(models.Model):

    """Model to view ordered articles in menu"""
    article = models.OneToOneField(Article, primary_key=True)
    position = models.IntegerField(unique=True)
