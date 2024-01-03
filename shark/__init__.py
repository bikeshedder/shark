from django.conf import settings
from django.urls import reverse


try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata
try:
    __version__ = importlib_metadata.version(__name__)
except:
    __version__ = "unknown"


def get_admin_change_url(obj):
    meta = obj._meta
    app_label = meta.app_label
    model_name = meta.model_name
    view_name = "admin:%s_%s_change" % (app_label, model_name)
    return reverse(view_name, args=(obj.pk,))


def get_admin_changelist_url(obj):
    meta = obj._meta
    app_label = meta.app_label
    model_name = meta.model_name
    view_name = "admin:%s_%s_changelist" % (app_label, model_name)
    return reverse(view_name)
