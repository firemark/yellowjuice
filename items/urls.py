from django.conf.urls import patterns, url
from items import views

urlpatterns = patterns(
    '',
    url(r'^$', views.show_items, name='show'),
    url(r'update/$', views.update_items, name='update')
)
