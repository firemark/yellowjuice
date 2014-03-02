from django import forms
from .models import Article, DraftTranslation
from langs.models import Language
from django.contrib.auth import get_user_model

User = get_user_model()


def get_length(model, name):
    return model._meta.get_field_by_name(name)[0].max_length


class AuthorList(object):

    """Show only user with is_translator flag"""

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        qs = User.objects.filter(is_translator=True)
        self.fields['author'].queryset = qs


class AddArticleForm(AuthorList, forms.ModelForm):

    slug = forms.SlugField(max_length=get_length(DraftTranslation, 'slug'))
    title = forms.CharField(max_length=get_length(DraftTranslation, 'title'))
    lang = forms.ModelChoiceField(queryset=Language.objects.all(),
                                  required=True)
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Article
        fields = ('author', 'lang', 'slug', 'title', 'text')

    def save(self, commit=True):
        article = super().save()
        article.translations.create(**self.cleaned_data)

        return article

    def save_m2m(self):
        """Admin panel call this method - doing nothing"""
        pass


class EditTranslationForm(AuthorList, forms.ModelForm):

    class Meta:
        model = DraftTranslation
        exclude = ('article', 'lang')


class AddTranslationForm(AuthorList, forms.ModelForm):

    class Meta:
        model = DraftTranslation
        exclude = ('article',)
