import inspect

from django.conf import settings

from shark.utils.importlib import import_object

RAISE_ERROR = object()


def get_settings_value(name, default=RAISE_ERROR):
    d = settings.SHARK
    parts = name.split(".")
    for part in parts:
        try:
            d = d[part]
        except KeyError:
            if default is RAISE_ERROR:
                raise KeyError(
                    "No such setting: settings.SHARK%s"
                    % "".join("[%r]" % part for part in parts)
                )
            return default
    return d


def get_settings_instance(name):
    try:
        v = settings[name]
        if isinstance(v, str):
            v = import_object(v)
        if inspect.isclass(v):
            v = v()
        return v
    except KeyError:
        return None
