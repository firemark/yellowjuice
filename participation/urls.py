from django.conf.urls import patterns, url
from participation import views

urlpatterns = patterns(
    '',
    url(r'^$', views.show_participations, name='show'),
    url(r'^new/$', views.edit_participation, name='new'),
    url(r'^restore/(?P<is_true>yes|no)/$',
        views.restore_participations, name='restore'),
    url(r'^edit/(?P<pk>\d+)/$', views.edit_participation, name='edit'),
    url(r'^del/(?P<pk>\d+)/$', views.delete_participation, name='delete')
)
