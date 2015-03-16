from django.conf import settings


RAISE_ERROR = object()


def get_settings_value(name, default=RAISE_ERROR):
    d = settings.SHARK
    parts = name.split('.')
    for part in parts:
        try:
            d = d[part]
        except KeyError:
            if default is RAISE_ERROR:
                raise KeyError('No such setting: settings.SHARK%s' % ''.join('[%r]' % part for part in parts))
            return default
    return d


def shark_settings(d, base=None):
    if not base:
        from shark import settings_base
        base = settings_base.SHARK
    settings = base.copy()
    for key, value in d.iteritems():
        if isinstance(value, dict):
            if not isinstance(base.get(key, {}), dict):
                raise RuntimeError('Type mismatch of settings and base settings: %r' % key)
            settings[key] = shark_settings(value, base.get(key, {}))
        else:
            settings[key] = value
    return settings
