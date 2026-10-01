FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BERKIOS_ENV=production

WORKDIR /app

COPY pyproject.toml README.md VERSION ./
COPY berkios ./berkios

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

RUN useradd --create-home --uid 10001 berkios \
    && mkdir -p /var/lib/berkios \
    && chown -R berkios:berkios /app /var/lib/berkios

USER berkios

EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=5s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()"

CMD ["python", "-m", "berkios"]
