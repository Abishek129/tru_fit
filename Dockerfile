# ---- base image ----
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# ---- deps layer (cache) ----
FROM base AS deps
COPY requirements.txt .
RUN python -m pip install --upgrade pip wheel setuptools \
 && pip install -r requirements.txt

# ---- runtime ----
FROM base
COPY --from=deps /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=deps /usr/local/bin /usr/local/bin
COPY . /app

# non-root
RUN useradd -m app && chown -R app:app /app
USER app

# Gunicorn (ASGI) — no migrate/collectstatic here
CMD ["gunicorn","trufit_backend.asgi:application","-k","uvicorn.workers.UvicornWorker","--bind","0.0.0.0:8000","--workers","2","--timeout","60"]
