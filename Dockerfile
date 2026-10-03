# syntax=docker/dockerfile:1
#
# Kalagana runtime image — serves the offline REST API.
#
#   docker build -t kalagana .
#   docker run --rm -p 8765:8765 kalagana
#   curl http://127.0.0.1:8765/health
#
# Configuration is read from the environment (see .env.example):
#   docker run --rm -p 8765:8765 -e KALAGANA_CITY=mumbai kalagana
FROM python:3.13-slim

LABEL org.opencontainers.image.title="Kalagana" \
      org.opencontainers.image.description="Offline Hindu (Drik) panchang, muhurta and festival calculator REST API" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/mitjangid/Kalagana"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    KALAGANA_HOST=0.0.0.0 \
    KALAGANA_PORT=8765

WORKDIR /app

# Package metadata first (better layer caching), then the source.
COPY pyproject.toml README.md MANIFEST.in LICENSE ./
COPY kalagana ./kalagana

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir .

EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import sys,urllib.request;sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8765/health',timeout=3).status==200 else 1)"

# `kalagana serve` starts the API; host/port come from the environment above.
ENTRYPOINT ["kalagana"]
CMD ["serve"]
