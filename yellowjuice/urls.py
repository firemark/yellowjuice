from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

panel_urls = patterns(
    '',
    url(r'^$', 'participation.views.show_participations', name='panel'),
    url(r'^participation/', include('participation.urls',
                                    namespace='participation')),
    url(r'^prelections/', include('agendas.urls',
                                  namespace='prelection')),
    url(r'^items/', include('items.urls',
                            namespace='item')),

)

urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='main.html'), name='home'),
    url(r'^panel/', include(panel_urls)),
    #.html for seo
    url(r'^art/(?P<slug>[\w\-_.]+)-(?P<pk>[0-9]+)\.html',
        'articles.views.show', name='article-show'),
    url(r'lang/set/(?P<code>[\w\-]+)$', 'langs.views.change_language',
        name='change-language'),

    url(r'^login/$', 'django.contrib.auth.views.login', {
        'template_name': 'login.html'}),
    url(r'^logout/$',
        'django.contrib.auth.views.logout',
        {'next_page': '/'}),
    url(r'^sign-up/$', 'main.views.signup', name='signup'),
    url(r'^confirm/(?P<hash_key>[0-9a-f]+)/$', 'main.views.confirm',
        name='confirm'),
    url(r'^sign-up/done/$',
        TemplateView.as_view(template_name='signup_done.html'),
        name='signup-done'
        ),
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
