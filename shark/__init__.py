from django.conf import settings
from django.urls import reverse

__version__ = '0.0.1'


def get_admin_change_url(obj):
    meta = obj._meta
    app_label = meta.app_label
    model_name = meta.model_name
    view_name = 'admin:%s_%s_change' % (app_label, model_name)
    return reverse(view_name, args=(obj.pk,))


def get_admin_changelist_url(obj):
    meta = obj._meta
    app_label = meta.app_label
    model_name = meta.model_name
    view_name = 'admin:%s_%s_changelist' % (app_label, model_name)
    return reverse(view_name)
