from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'shark.views.home', name='home'),
    # url(r'^shark/', include('shark.foo.urls')),
    url(r'^admin/billing/', include('shark.billing.admin_urls', namespace='billing_admin')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
)
