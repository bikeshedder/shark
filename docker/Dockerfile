FROM python:3.12-bookworm AS base

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_HOME="/opt/poetry"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN apt update && apt install -y \
  curl \
  build-essential \
  python3-dev \
  libmagickwand-dev

ARG POETRY_VERSION=1.8.3

RUN --mount=type=cache,target=/root/.cache \
  curl -sSL https://install.python-poetry.org | POETRY_VERSION=$POETRY_VERSION python

WORKDIR /app

COPY poetry.lock poetry.toml pyproject.toml .

RUN --mount=type=cache,target=/root/.cache poetry install --only main

COPY . .

COPY docker/entrypoint.sh .
ENTRYPOINT ["bash", "/app/entrypoint.sh"]
