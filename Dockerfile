# syntax=docker/dockerfile:1

FROM python:3.13-slim

# Pinned uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install dependencies first to leverage layer caching
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy the application (keeps repo layout: /app/src and /app/img_anteojos)
COPY src ./src
COPY img_anteojos ./img_anteojos
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh

# Collect static files at build time (no DB access needed; SQLite fallback)
RUN DATABASE_URL= python src/manage.py collectstatic --noinput

# Run as an unprivileged user; media dir must be writable for uploaded images
RUN useradd --create-home --uid 1000 app \
    && mkdir -p /app/src/media \
    && chown -R app:app /app/src/media \
    && chmod +x /usr/local/bin/entrypoint.sh
USER app

WORKDIR /app/src
EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
