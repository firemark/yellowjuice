from django.conf.urls import patterns, url
import agendas.views as views

urlpatterns = patterns(
    '',
    url(r'^$', views.show_prelections, name='show'),
    url(r'^new/$', views.edit_prelection, name='new'),
    url(r'^edit/(?P<pk>\d+)/$', views.edit_prelection, name='edit'),
    url(r'^del/(?P<pk>\d+)/$', views.delete_prelection, name='delete')
)