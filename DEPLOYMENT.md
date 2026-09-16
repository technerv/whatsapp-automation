# Deployment

## Production configuration

Set `DEBUG=False` and provide a strong `SECRET_KEY`. The application fails fast
when production starts without one. Configure `ALLOWED_HOSTS`,
`CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` with production origins.

Operational checks:

```text
GET /healthz/  -> process health
GET /readyz/   -> process and database readiness
```

Before release:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

Run Django behind a production WSGI/ASGI server and reverse proxy. Do not use
`runserver` in production. Keep M-PESA, WhatsApp, JWT, database, and AI secrets
in the deployment secret manager, never in Git.