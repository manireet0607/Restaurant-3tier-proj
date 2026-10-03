FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Amazon RDS CA bundle, used for TLS certificate verification (DB_SSL_CA=/certs/global-bundle.pem)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && mkdir -p /certs \
    && curl -fsSL https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -o /certs/global-bundle.pem \
    && apt-get purge -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

COPY . .
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Migrate, seed (safe to repeat), then start the API.
CMD ["sh", "-c", "alembic upgrade head && python -m app.db.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers"]
