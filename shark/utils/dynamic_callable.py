from importlib import import_module


def dynamic_callable(name):
    module_name, function_name = name.rsplit('.', 1)
    def wrapped(*args, **kwargs):
        module = import_module(module_name)
        function = getattr(module, function_name)
        return function(*args, **kwargs)
    wrapped.__name__ == function_name
    return wrapped
