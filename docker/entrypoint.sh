uv run python manage.py migrate
uv run python manage.py collectstatic --noinput --turbo
uv run gunicorn --workers 1 --threads 8 --timeout 120 -b 0.0.0.0:8000 "shark.wsgi"
