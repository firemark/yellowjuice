from django import forms
from .models import Participant


class ParticipantForm(forms.ModelForm):

    birthday = forms.DateField(
        input_formats=["%d-%m-%y"],
        help_text="Format is DD-MM-YYYY",
        required=False
    )

    class Meta:
        model = Participant
        fields = ('first_name', 'last_name', 'birthday', 'phone', 'address')
