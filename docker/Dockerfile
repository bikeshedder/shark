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

# install UV
ARG UV_VERSION=0.6.11
RUN python3.12 -m venv /opt/uv && \
    /opt/uv/bin/pip install uv==$UV_VERSION && \
    ln -s /opt/uv/bin/uv /usr/local/bin/uv

RUN adduser debian
USER debian

WORKDIR /app
COPY pyproject.toml uv.lock .
RUN uv sync

COPY . .
#RUN uv build

ENTRYPOINT ["/app/docker-entrypoint.py"]
