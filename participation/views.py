from .forms import ParticipantForm
from misc.views import AbstractEditView, AbstractDeleteView
from django.shortcuts import render, redirect
from .models import Participation
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required

import logging

log = logging.getLogger('participation.views')


@login_required
def show_participations(request):
    present_participations = Participation.objects.present_with_req(request)

    user = request.user
    conf = request.conference
    old_participations = None

    if request.user.last_conference is None:
        user.last_conference = conf
        user.save()
    elif user.last_conference.id != conf.id:
        old_participations = Participation.objects.old_with_req(request)

        if len(old_participations) == 0:
            user.last_conference = conf
            user.save()

    return render(request, "panel/participation/show.html", {
        'old_participations': old_participations,
        'participations': present_participations.all()
    })


@login_required
def restore_participations(request, is_true):
    user = request.user
    conf = request.conference

    user.last_conference = conf
    user.save()

    if is_true == "yes":
        Participation.objects\
            .old_participations(request).update(conference=conf)

    return redirect("participation:show")


class ParticipationView(object):
    model_class = Participation
    redirect_url = "participation:show"

    def get_obj(self, request, pk, *args, **kwargs):
        if pk:
            obj = self.model_class.objects.present_with_req(request).get(pk=pk)
            return obj.participant
        else:
            return None


class EditParticipationView(ParticipationView, AbstractEditView):
    form_class = ParticipantForm
    template_name = "panel/participation/edit.html"

    def save(self, request, form, *args, **kwargs):
        participant = form.instance
        if participant.pk is None:
            participant.user = request.user
            participant.save()

            participation = Participation.objects.create(
                participant=participant,
                conference=request.conference
            )
            participation.save()
        else:
            form.save()

    def generate_successful_msg(self, request, obj, *args, **kwargs):
        if obj.pk is None:
            msg = _("New participant '%s' was addded")
        else:
            msg = _("Participant '%s' was changed")

        return msg % obj.full_name

edit_participation = EditParticipationView.as_view()


class DeleteParticipationView(ParticipationView, AbstractDeleteView):

    template_name = "panel/participation/delete.html"

    def generate_successful_msg(self, request, obj, *args, **kwargs):
        return _("Participant '%s' was deleted") % obj.full_name

delete_participation = DeleteParticipationView.as_view()
