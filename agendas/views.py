from .models import Prelection, PrelectionFile
from participation.models import Participant
from .forms import PrelectionForm
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from misc.views import AbstractEditView, AbstractDeleteView
from django.forms.models import inlineformset_factory


@login_required
def show_prelections(request):
    prelections = Prelection.objects.can_see(request.user, request.conference)
    return render(request, "panel/prelection/show.html", {
        "prelections": prelections
    })


class PrelectionView(object):
    model_class = Prelection
    redirect_url = "prelection:show"


class EditPrelectionView(PrelectionView, AbstractEditView):
    form_class = PrelectionForm
    template_name = "panel/prelection/edit.html"
    files_formset = inlineformset_factory(Prelection, PrelectionFile,
                                          fields=['title', 'file'])

    def get_form(self, request, obj, data, *args, **kwargs):

        datas = (data, request.FILES) if request.method == "POST" else (data,)

        form = self.form_class(
            *datas,
            instance=obj,
            initial=self.initial,
            prelectors=Participant.objects.can_see_with_req(request)
        )

        form.files = self.files_formset(*datas, instance=obj, prefix="files")

        return form

    def is_valid(self, request, form, *args, **kwargs):
        return form.is_valid() and form.files.is_valid()

    def save(self, request, form, *args, **kwargs):
        obj = form.instance
        if obj.pk is None:
            obj.conference = request.conference
            form.files.instance = obj

        form.save()
        form.files.save()

    def generate_successful_msg(self, request, obj, *args, **kwargs):
        if obj.pk is None:
            msg = _("New prelection '%s' was added.")
        else:
            msg = _("Prelection '%s' was changed.")

        return msg % obj.title

edit_prelection = EditPrelectionView.as_view()


class DeletePrelectionView(PrelectionView, AbstractDeleteView):
    template_name = "panel/prelection/delete.html"

    def generate_successful_msg(self, request, obj, *args, **kwargs):
        return _("Prelections '%s' was deleted") % obj.title

delete_prelection = DeletePrelectionView.as_view()
