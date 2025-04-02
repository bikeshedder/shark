FROM python:3.12-bookworm AS base

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

RUN apt update && apt install -y \
  curl \
  build-essential \
  python3-dev \
  libmagickwand-dev

RUN adduser debian
USER debian

ARG UV_VERSION=0.6.11
RUN curl -LsSf https://astral.sh/uv/$UV_VERSION/install.sh | sh

WORKDIR /code
COPY pyproject.toml uv.lock .
RUN /home/debian/.local/bin/uv sync

COPY . .
#RUN /home/debian/.local/bin/uv build

COPY docker/entrypoint.sh .
ENTRYPOINT ["bash", "/app/entrypoint.sh"]
