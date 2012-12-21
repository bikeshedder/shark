from django.conf import settings


def get_model(name):
    MODELS = settings.SHARK.get('MODELS', {})
    name = MODELS.get(name, name)
    app_label, model_name = name.split('.', 2)
    from django.db import models
    return models.get_model(app_label, model_name)
