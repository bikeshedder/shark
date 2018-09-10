from django.conf import settings
from django.urls import reverse


def get_model(name):
    name = get_model_name(name)
    app_label, model_name = name.split('.', 2)
    from django.apps import apps
    return apps.get_model(app_label, model_name)


def get_model_name(name):
    MODELS = settings.SHARK.get('MODELS', {})
    return MODELS.get(name, name)


def is_model_overridden(name):
    return get_model_name(name) != name


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
