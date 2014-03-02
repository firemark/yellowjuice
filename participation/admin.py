from django.contrib import admin
from misc.mail import send_email
from .models import Participant, Participation
try:
    from items.models import Option
except ImportError:
    Option = None


class OptionInline(admin.TabularInline):
    model = Option
    extra = 0


class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 0
    ordering = ('conference__start',)
    fields = ('conference', 'status')


class ParticipationAdmin(admin.ModelAdmin):
    inlines = (OptionInline,) if Option else ()

    list_display = ('first_name', 'last_name',
                    'email', 'conference', 'status')

    list_display_links = ('first_name', 'last_name', 'email')
    list_filter = ('status',)
    list_select_related = True
    search_fields = ('participant__last_name',
                     'participant__first_name',
                     'participant__user__email')
    ordering = ('conference__start', 'participant__last_name',
                'participant__first_name', )

    def email(self, obj):
        return obj.participant.user.email
    email.admin_order_field = 'partcitipant__user__email'

    def first_name(self, obj):
        return obj.participant.first_name
    first_name.admin_order_field = 'partcitipant__first_name'

    def last_name(self, obj):
        return obj.participant.last_name
    last_name.admin_order_field = 'participant__last_name'

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Participation.objects.get(pk=obj.pk)
            if old_obj.status != obj.status:
                send_email("Changed status", "email/participation/status.txt",
                           {
                           "old_status": old_obj.get_status_display(),
                           "new_status": obj.get_status_display(),
                           "full_name": obj.participant.full_name
                           },
                           [obj.participant.user.email])
        obj.save()


class ParticipantAdmin(admin.ModelAdmin):
    inlines = (ParticipationInline,)
    list_display = ('first_name', 'last_name', 'email', 'address')
    list_display_links = ('first_name', 'last_name')
    list_select_related = True
    search_fields = ('first_name', 'last_name', 'user__email')

    ordering = ('last_name', 'first_name')

    def email(self, obj):
        return obj.user.email
    email.admin_order_field = 'user__email'

admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Participation, ParticipationAdmin)
