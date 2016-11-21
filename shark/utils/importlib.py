from importlib import import_module


def import_object(name):
    module_name, object_name = name.rsplit('.', 1)
    module = import_module(module_name)
    return getattr(module, object_name)
