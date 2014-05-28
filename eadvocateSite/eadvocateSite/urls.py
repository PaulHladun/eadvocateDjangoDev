from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'eadvocateSite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),   
    url(r'^$', TemplateView.as_view(template_name="index.html"), name="index"),
    url(r'^howWeHelp/$', TemplateView.as_view(template_name="howWeHelp.html"), name="howWeHelp"),
    url(r'^findCare/$', TemplateView.as_view(template_name="findCare.html"), name="findCare"),
    url(r'^findWork/$', TemplateView.as_view(template_name="findWork.html"), name="findWork"),
    url(r'^client_dashboard/$', TemplateView.as_view(template_name="client_dashboard.html"), name="client_dashboard"),
    url(r'^cp_dashboard/$', TemplateView.as_view(template_name="cp_dashboard.html"), name="cp_dashboard"),
    url(r'^rfc_contract/$', TemplateView.as_view(template_name="rfc_contract.html"), name="rfc_contract"),
    url(r'^rfc_form/$', TemplateView.as_view(template_name="rfc_form.html"), name="rfc_form"), 
    url(r'^rfc_response/$', TemplateView.as_view(template_name="rfc_response.html"), name="rfc_response"),     
)

#from django.conf import settings

#if settings.DEBUG:
    #urlpatterns += patterns('django.contrib.staticfiles.views',
        #url(r'^static/(?P<path>.*)$', 'serve'),
    #)