from django.contrib import admin
from .models import User, Conference, Currency, UserConfirm
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls import patterns, url
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from time import strptime
from datetime import datetime
from .settings import TIMEDELTA

try:
    from participation.models import Participant
except ImportError:
    has_participant = False
else:
    has_participant = True


class ParticipantInline(admin.TabularInline):
    model = Participant if has_participant else None

    def has_add_permission(self, request):
        return False

    def has_edit_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_administrator', 'is_organizator',
                    'is_reviewer', 'is_translator', 'is_active',
                    'is_staff', 'is_superuser')
    list_filter = ('is_administrator', 'is_organizator',
                   'is_reviewer', 'is_translator', 'is_active',
                   'is_staff', 'is_superuser')
    search_fields = ('email',)
    inlines = (ParticipantInline,) if has_participant else ()


class ConferenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'start', 'end', 'open_for_prelection',
                    'open_register', 'is_active', 'agenda')

    class Media:
        js = ('javascript/vendor/jquery-1.10.2.js',
              'javascript/vendor/jquery-ui-1.10.2.js')

    def agenda(self, obj):
        return '<a href="%s" class="btn btn-small">Show agenda</a>' % (
            reverse("admin:agenda", args=(obj.pk,))
        )
    agenda.allow_tags = True

    def get_urls(self):
        urls = patterns('',
                        url(r'^([^/]+)/agenda$',
                            self.admin_site.admin_view(self.agenda_view),
                            name='agenda'),
                        url(r'^([^/]+)/agenda/save/$',
                            self.admin_site.admin_view(self.agenda_view_save),
                            name='agenda-save-all'))

        return urls + super().get_urls()

    def agenda_view(self, request, pk_conference):

        conference = get_object_or_404(Conference, pk=pk_conference)

        return render(request,
                      "admin/conference/agenda.html",
                      {
                          "conference": conference,
                          "media": self.media,
                          "TIMEDELTA": TIMEDELTA,
                          "opts": self.opts,
                          "add": False,
                          "has_change_permission": True
                      })

    @csrf_exempt
    def agenda_view_save(self, request, pk_conf):
        conf = get_object_or_404(Conference, pk=pk_conf)
        if request.method == "POST":
            agenda = request.POST.getlist('agenda[]')
            for pk, raw_time, room_pk in (data.split('/') for data in agenda):
                prelection = conf.prelections.get(pk=pk)
                dt = strptime(raw_time, "%Y-%m-%d %H:%M")
                prelection.time = datetime(dt.tm_year,
                                           dt.tm_mon,
                                           dt.tm_mday,
                                           dt.tm_hour,
                                           dt.tm_min)
                room = conf.rooms.get(pk=room_pk) if room_pk != 'X' else None
                prelection.room = room

                prelection.save()

            not_added = request.POST.getlist('not_added[]')
            for pk in not_added:
                prelection = conf.prelections.get(pk=pk)
                prelection.accept()
                prelection.save()

            return HttpResponse()  # send nothing
        else:
            raise PermissionDenied


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name',)


admin.site.register(User, UserAdmin)
admin.site.register(UserConfirm)
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(Currency, CurrencyAdmin)
