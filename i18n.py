#!/usr/bin/env -S poetry run python

import os
import sys

import django
from django.conf import settings

settings.configure(SECRET_KEY="DOES_NOT_MATTER")
django.setup()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

django.setup()

# Paths to search for translatable apps
SEARCH_PATHS = ["shark"]

# Map i18n commands to Django management commands
COMMANDS = {
    "update": (
        "makemessages",
        {
            "all": True,
            "extensions": ["py", "html", "txt", "subject", "body"],
        },
    ),
    "compile": (
        "compilemessages",
        {
            "locale": None,
        },
    ),
}


def log(s):
    sys.stderr.write("%s\n" % s)


def call(app, func):
    cwd = os.getcwd()
    try:
        os.chdir(app)
        return func()
    finally:
        os.chdir(cwd)


def find_i18n_apps(paths=SEARCH_PATHS):
    apps = []
    for path in paths:
        if not os.path.abspath(path).startswith(PROJECT_ROOT):
            continue
        path = os.path.normpath(path)
        for root, dirnames, filenames in os.walk(path):
            if "locale" in dirnames:
                apps.append(root)
    return apps


if __name__ == "__main__":
    from django.core.management import call_command

    usage = """Usage: i18n CMD [APPS]...

    i18n update         update all .po files in all apps
    i18n compile        compile all .mo files in all apps

    i18n CMD foo bar    run CMD on apps foo and bar
    """

    try:
        args = sys.argv[1:]
        cmd = args.pop(0)
        cmd, options = COMMANDS[cmd]
    except Exception:
        log(usage)
        sys.exit(1)

    for app in find_i18n_apps(args or SEARCH_PATHS):
        log(">>> %s" % app)
        call(app, lambda: call_command(cmd, **options))
