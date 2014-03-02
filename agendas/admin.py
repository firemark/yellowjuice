from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from .models import Prelection, ReviewerComment, Room, RoomTranslate
from .forms import ReviewerCommentForm
from django.utils.text import Truncator
from misc.mail import send_email


class CommentInline(admin.TabularInline):
    model = ReviewerComment
    form = ReviewerCommentForm
    fields = ('content', 'author')
    readonly_fields = ('author', )
    extra = 0


class RoomTranslateInline(admin.TabularInline):
    model = RoomTranslate
    extra = 1


class PrelectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_description', 'main_prelector', 'time',
                    'status', 'length', 'conference')
    readonly_fields = ('main_prelector', 'other_prelectors', 'conference')

    fields = ('main_prelector', 'other_prelectors',
              'title', 'description', 'status', 'time', 'length', 'conference')

    inlines = (CommentInline,)

    def short_description(self, obj):
        return Truncator(obj.description).chars(30)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            try:
                getattr(obj, 'author')
            except ObjectDoesNotExist:
                obj.author = request.user
            obj.save()
        formset.save_m2m()

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Prelection.objects.get(pk=obj.pk)
            if old_obj.status != obj.status:
                send_email("Changed status", "email/prelection/status.txt",
                           {
                           "old_status": old_obj.get_status_display(),
                           "new_status": obj.get_status_display(),
                           "title": obj.title
                           },
                           [obj.main_prelector.user.email])
        obj.save()


class RoomAdmin(admin.ModelAdmin):
    list_display = ('key', 'conference')
    inlines = (RoomTranslateInline,)

admin.site.register(Prelection, PrelectionAdmin)
admin.site.register(Room, RoomAdmin)
