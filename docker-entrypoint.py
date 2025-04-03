#!/usr/bin/env -S uv run python
# ruff: noqa: T201

import os
import socket
import subprocess
import sys

import click
import django
import httpx
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.core.management import execute_from_command_line


def wait_for_postgresql():
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect(
                (
                    settings.DATABASES["default"]["HOST"],
                    int(settings.DATABASES["default"]["PORT"]),
                )
            )
        except OSError:
            print("PostgreSQL is unavailable - sleeping", file=sys.stderr)
            continue
        s.close()
        print("PostgreSQL is up - continuing...", file=sys.stderr)
        return


@click.group()
def cli():
    pass


@cli.command()
def install():
    wait_for_postgresql()
    execute_from_command_line(["django-admin", "migrate", "--no-input"])
    execute_from_command_line(["django-admin", "collectstatic", "--no-input"])


@cli.command()
def update():
    wait_for_postgresql()
    execute_from_command_line(["django-admin", "migrate", "--no-input"])
    execute_from_command_line(["django-admin", "collectstatic", "--no-input"])


@cli.group()
def test():
    pass


@test.command("postgres")
def test_postgres():
    django.setup(set_prefix=False)
    from django.db import connection

    print("Testing PostgreSQL connection")
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        if cursor.fetchone() == (1,):
            print("  [Ok]")


@test.command("s3")
def test_s3():
    django.setup(set_prefix=False)

    filename = "test.txt"
    content = b"test"

    # create file
    print(f"Creating file: {filename}")
    default_storage.save(filename, ContentFile(content))
    print("  [Ok]")

    # test endpoint URL
    url = f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET_MEDIA}/{filename}"
    print(f"Testing with S3_ENDPOINT_URL: {url}")
    rsp = httpx.get(url)
    print("  [Ok]" if rsp.status_code == 200 else f"  [Error: {rsp.status_code}]")

    # test public URL
    public_url = f"{settings.S3_PUBLIC_URL}/{filename}"
    print(f"Testing with S3_PUBLIC_URL: {public_url}")
    rsp = httpx.get(public_url)
    print("  [Ok]" if rsp.status_code == 200 else f"  [Error: {rsp.status_code}]")

    # delete file
    print(f"Deleting file: {filename}")
    default_storage.delete(filename)
    print("  [Ok]")


@cli.group()
def start():
    pass


@start.command("server")
def start_server():
    wait_for_postgresql()
    subprocess.check_call(
        [
            "gunicorn",
            "shark.wsgi:application",
            "--bind",
            "0.0.0.0:8000",
        ]
    )


@cli.command(
    context_settings=dict(
        help_option_names=[],
        ignore_unknown_options=True,
    )
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def django_admin(args):
    execute_from_command_line(["django-admin", *args])


@test.command("email")
@click.argument("email_address")
def test_email(email_address):
    print(f"Sending email to: {email_address} ...")
    send_mail("Test", "Test", settings.DEFAULT_FROM_EMAIL, [email_address])
    print("Done.")


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shark.settings")
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    cli()
