from django.contrib import admin
from .models import DraftTranslation, Article, PublishedTranslation, Menu
from django.conf.urls import patterns, url
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.contrib import messages
from .forms import AddArticleForm, AddTranslationForm, EditTranslationForm
from .templatetags.translation import status_on_list
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('pk',  '__str__')
    list_display_link = ('pk', '__str__')
    add_form_template = 'admin/change_form.html'
    change_form_template = 'admin/article/change.html'

    def get_form(self, request, obj=None, **kwargs):
        """If article is new - change form"""
        if obj and obj.pk:
            return super().get_form(request, obj, **kwargs)
        else:
            return AddArticleForm

    def change_view(self, request, object_id, form_url='', extra_context=None):
        translations = DraftTranslation.objects\
            .select_related('published', 'author')\
            .filter(article=object_id)

        context = extra_context or {}
        context.update({"translations": translations})

        return super().change_view(request, object_id, form_url, context)


class DraftTranslationAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'lang', 'posted_date',
                    'edited_date', 'published_date', 'status')
    list_display_without_perms = list_display[:-1] + ('status_without_perms',)
    list_display_link = ('title',)

    ordering = ('title',)
    search_fields = ('title',)

    add_form_template = 'admin/translation/change.html'
    change_form_template = 'admin/translation/change.html'

    # columns in a list

    def status(self, obj):
        """View status in the cell"""
        return status_on_list(obj, has_perm=True)
    status.allow_tags = True

    def status_without_perms(self, obj):
        return status_on_list(obj, has_perm=False)
    status_without_perms.allow_tags = True
    status_without_perms.short_description = 'Status'

    def get_list_display(self, request):
        if request.user.has_perm('articles'):
            return self.list_display
        return self.list_display_without_perms

    def queryset(self, request):
        qs = super().queryset(request)
        user = request.user
        if user.has_perm('articles'):
            return qs
        else:
            return qs.filter(author=user)

    def published_date(self, obj):
        try:
            return obj.published.publish_date
        except PublishedTranslation.DoesNotExist:
            return "-"

    def admin_url(self, regexp, view, name):
        return url(regexp, self.admin_site.admin_view(view), name=name)

    def get_urls(self):
        urls = patterns('',
                        self.admin_url(r'^([^/]+)/publish/$',
                                       self.publish_view,
                                       'publish-translation'),
                        self.admin_url(r'^add-by-article/(.+)$',
                                       self.add_by_article,
                                       'add-by-article'),
                        self.admin_url(r'^([^/]+)/change-by-article/(.+)$',
                                       self.change_by_article,
                                       'change-by-article'))

        return urls + super().get_urls()

    def get_form(self, request, obj=None, **kw):
        """If translation is new - show change language"""
        if not (obj and obj.pk):
            if request.article_pk:
                return AddTranslationForm
        else:
            return EditTranslationForm
        return super().get_form(request, obj, **kw)

    def has_change_permission(self, request, obj=None):
        user = request.user
        return user.has_perm('articles') or obj.author == user if obj else True

    # views
    def add_by_article(self, request, pk):
        return self.add_view(request, article_pk=pk)

    def change_by_article(self, request, obj_pk, article_pk):
        return self.change_view(request, obj_pk, article_pk=article_pk)

    def add_view(self, request, form_url='', extra_context=None,
                 article_pk=None):
        """add article_pk to request
        little hack to send to new traslation a pk of article"""
        request.article_pk = article_pk
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None,
                    article_pk=None):
        request.article_pk = article_pk
        return super().change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        article_pk = request.article_pk
        if article_pk and not obj.pk:
            obj.article = Article(pk=article_pk)
        obj.save()

    def response(self, action, request, obj, **kwargs):
        """DRY rule"""

        method = getattr(super(), 'response_%s' % action)
        response = method(request, obj, **kwargs)

        if not request.article_pk:
            return response
        else:
            article_pk = obj.article.pk
            url = reverse("admin:articles_article_change", args=[article_pk])

            return HttpResponseRedirect(url)

    def response_change(self, request, obj):
        return self.response('change', request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        return self.response('add', request, obj,
                             post_url_continue=post_url_continue)

    def publish_view(self, request, pk):
        obj = get_object_or_404(DraftTranslation, pk=pk)

        try:
            try:
                is_new = bool(obj.published)
            except PublishedTranslation.DoesNotExist:
                is_new = False

            obj.publish()
        except ValidationError as e:
            errors = e.message_dict
            self.message_user(request,
                              'Translation has errors:',
                              messages.ERROR)
            for name, msgs in errors.items():
                self.message_user(request,
                                  '%s: %s' % (name, ' | '.join(msgs)),
                                  messages.ERROR)

        else:
            self.message_user(
                request,
                'Translation was %s' % ('published' if is_new else 'updated'),
                messages.SUCCESS
            )

        reverse_url = reverse('admin:articles_drafttranslation_change',
                              args=[pk])

        url = request.META.get('HTTP_REFERER', reverse_url)

        return HttpResponseRedirect(url)


class MenuAdmin(admin.ModelAdmin):

    change_list_template = 'admin/menu/list.html'
    ordering = ('position',)

    class Media:
        js = ('javascript/vendor/jquery-1.10.2.js',
              'javascript/vendor/jquery-ui-1.10.2.js')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return not bool(obj)

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        articles = Article.objects\
            .filter(visible=True)\
            .exclude(id__in=self.queryset(request))

        extra_context.update({'articles': articles})
        return super().changelist_view(request, extra_context)

    def queryset(self, request):
        return Menu.objects\
            .select_related('article__pk')\
            .filter(article__visible=True)

    def get_urls(self):
        urls = patterns('', url(r'^save-all/$',
                                self.admin_site.admin_view(self.save_all),
                                name='menu-save-all'))

        return urls + super().get_urls()

    @csrf_exempt
    def save_all(self, request):
        if request.method == "POST":
            Menu.objects.all().delete()  # delete all menu to rewrite

            # create a new menu
            pk_list = request.POST.getlist('menu[]')
            menu = [Menu(pk, i) for i, pk in enumerate(pk_list)]
            Menu.objects.bulk_create(menu)

            return HttpResponse()  # send nothing
        else:
            raise PermissionDenied


admin.site.register(DraftTranslation, DraftTranslationAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Menu, MenuAdmin)
