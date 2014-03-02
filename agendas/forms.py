from django import forms
from django.utils.translation import ugettext as _
from .models import Prelection, ReviewerComment, PrelectionFile


class DisablableForm(object):

    """Form that can be disabled"""

    def __init__(self, *args, **kwargs):
        disabled = kwargs.pop('disabled', False)
        super().__init__(*args, **kwargs)
        self.disabled = disabled

    def get_disabled(self):
        return self._disabled

    def set_disabled(self, disabled=True):
        """Propagate the disabledness down to fields"""
        self._disabled = disabled
        if disabled:
            for field in self.fields.values():
                field.widget.attrs['readonly'] = True
                field.widget.attrs['disabled'] = True

    disabled = property(get_disabled, set_disabled)

    def is_valid(self):
        """Disabled forms are never valid"""
        if self.disabled:
            self.errors['__all__'] = "This form is disabled"
            return False
        else:
            return super().is_valid()


class PrelectionForm(DisablableForm, forms.ModelForm):

    class Meta:
        model = Prelection
        fields = ('main_prelector', 'other_prelectors', 'title', 'description',
                  'length')

    def __init__(self, *args, **kwargs):
        """restrict prelectors"""
        prelectors = kwargs.pop('prelectors')
        super().__init__(*args, **kwargs)
        for field in ('main_prelector', 'other_prelectors'):
            self.fields[field].queryset = prelectors

        self.fields["other_prelectors"].required = False
        if len(prelectors) == 1:
            self.fields['main_prelector'].initial = prelectors[0]

    def clean(self):
        data = super().clean()

        if data['main_prelector'] in data['other_prelectors']:
            raise forms.ValidationError(
                _("Main prelector mustn't be in other prelectors.")
            )
        return data


class ReviewerCommentForm(forms.ModelForm):

    """Form for commenting prelections"""
    class Meta:
        model = ReviewerComment
        fields = ('content', 'prelection', 'author')

    def __init__(self, *args, **kwargs):
        self.prelection = kwargs.pop('prelection', None)
        self.author = kwargs.pop('author', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.prelection is not None:
            obj.prelection = self.prelection
        if self.author is not None:
            obj.author = self.author
        if commit:
            obj.save()
            self.save_m2m()
        return obj
