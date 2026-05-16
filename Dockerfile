# Stage 1: builder
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --upgrade pip \
 && pip install --prefix=/install ".[prod]"

# Stage 2: runtime
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app \
    APP_HOME=/app \
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system --gid 1000 quiz \
    && useradd  --system --uid 1000 --gid quiz --home /app quiz

WORKDIR ${APP_HOME}

COPY --from=builder /install /usr/local

COPY --chown=quiz:quiz src/         ./src/
COPY --chown=quiz:quiz alembic/     ./alembic/
COPY --chown=quiz:quiz alembic.ini  ./
COPY --chown=quiz:quiz pyproject.toml ./

USER quiz

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; \
sys.exit(0 if urllib.request.urlopen('http://localhost:8000/healthz', timeout=3).status == 200 else 1)" \
    || exit 1

CMD ["sh", "-c", "alembic upgrade head && exec gunicorn \
    --bind 0.0.0.0:${PORT} \
    --workers 4 \
    --worker-class sync \
    --threads 2 \
    --timeout 60 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    'src.main:create_app()'"]
