from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

User = get_user_model()


def password_field(**kwargs):
    return forms.CharField(widget=forms.PasswordInput(), **kwargs)


class SignupForm(forms.ModelForm):

    password = password_field(
        label=_('Password'),
        required=True,
        min_length=6,
        help_text=_("Password must has at least 6 characters"))
    password_confirm = password_field(label=_('Confirm Password'),
                                      required=False)

    def clean(self):
        data = super(SignupForm, self).clean()
        password = data.get('password', '')
        password_confirm = data.get('password_confirm', '')

        if password and password != password_confirm:
            msg = _("Passwords are not same")
            self._errors["password"] = self.error_class([msg])

        return data

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm')
