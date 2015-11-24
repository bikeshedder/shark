from django.conf import settings
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/billing/', include('shark.billing.admin_urls', namespace='billing_admin')),
    url(r'^admin/sepa/', include('shark.sepa.admin_urls', namespace='sepa_admin')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^accounting/', include('shark.accounting.urls', namespace='accounting')),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url(r'^api/', include('shark.api_urls', namespace='api')),
)

if settings.DEBUG:
    # Serve media files when DEBUG is enabled
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
