from django.conf.urls import patterns, url
from myapp.views import AuthorCreate, AuthorUpdate, AuthorDelete

urlpatterns = patterns('',
    # ...
    url(r'author/add/$', AuthorCreate.as_view(), name='author_add'),
    url(r'author/(?P<pk>\d+)/$', AuthorUpdate.as_view(), name='author_update'),
    url(r'author/(?P<pk>\d+)/delete/$', AuthorDelete.as_view(), name='author_delete'),
)