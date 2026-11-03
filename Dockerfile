FROM python:3.12-slim

WORKDIR /app

# Dépendances d'abord : cette étape reste en cache tant que requirements.txt ne change pas
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --default-timeout=120 --retries 10 -r requirements.txt

COPY . .

# Ne pas faire tourner l'application en root
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
