# ---- builder (multi-arch friendly) ----
FROM --platform=$BUILDPLATFORM python:3.10-slim AS builder

ARG TARGETPLATFORM
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip wheel --wheel-dir /wheels -r requirements.txt

# ---- runtime ----
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UVICORN_WORKERS=4 \
    UVICORN_PORT=8000 \
    UVICORN_HOST=0.0.0.0

RUN adduser --disabled-password --gecos "" appuser && \
    apt-get update && apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
COPY --from=builder /wheels /wheels
RUN python -m pip install --upgrade pip && pip install --no-index --find-links=/wheels -r requirements.txt

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python - <<'PY' || exit 1
import sys, urllib.request
try:
    with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=3) as r:
        sys.exit(0 if r.status==200 else 1)
except Exception:
    sys.exit(1)
PY

CMD ["gunicorn","-k","uvicorn.workers.UvicornWorker","--workers","4","--timeout","60","--bind","0.0.0.0:8000","backend.app:app"]
