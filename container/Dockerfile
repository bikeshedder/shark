FROM python:3.11-bookworm AS base

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_HOME="/opt/poetry" \
  VENV_PATH="/opt/poetry/venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN apt update && apt install -y \
  curl \
  build-essential \
  python3-dev \
  libmagickwand-dev

RUN --mount=type=cache,target=/root/.cache \
  curl -sSL https://install.python-poetry.org | python

WORKDIR /app

COPY poetry.lock .
COPY pyproject.toml .

RUN --mount=type=cache,target=/root/.cache \
  . /opt/poetry/venv/bin/activate && poetry install --only main

COPY . .
RUN echo "source /opt/poetry/venv/bin/activate" >> ~/.bashrc

CMD gunicorn --workers 1 --threads 8 --timeout 120 -b 0.0.0.0:8000 "shark.wsgi"
