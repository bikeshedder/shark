import inspect

from django.utils import unittest


def import_testcases(module_name):
    '''
    Import test cases of a child module by adding it to this module
    prefixed with the name of the module.

    e.g. shark.foo.tests.FooTestCase becomes shark.tests.foo_FooTestCase
    and is then found by the test runner.
    '''
    shark_module = __import__('shark.%s.tests' % module_name)
    tests_module = getattr(shark_module, module_name).tests
    for name, value in tests_module.__dict__.items():
        if inspect.isclass(value) and issubclass(value, unittest.TestCase):
            globals()['%s_%s' % (module_name, name)] = value


import_testcases('utils')
