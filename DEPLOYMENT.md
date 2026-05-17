# Deployment

## Prerequisites

- Docker 24+ and Docker Compose v2
- A domain name with DNS pointing to your server
- SSL certificate (Let's Encrypt recommended)
- AWS S3 bucket (or compatible, e.g. Cloudflare R2) for media storage
- SMTP credentials for transactional email

## Quick Start (production)

```bash
# 1. Clone and enter the project
git clone <your-repo> pinboard && cd pinboard

# 2. Create your environment file
cp .env.example .env
# Edit .env — fill in SECRET_KEY, DB credentials, AWS keys, email settings

# 3. Place SSL certificates
mkdir -p docker/nginx/ssl
cp /path/to/fullchain.pem docker/nginx/ssl/
cp /path/to/privkey.pem  docker/nginx/ssl/

# 4. Update nginx server_name
sed -i 's/server_name _;/server_name yourdomain.com;/' docker/nginx/nginx.conf

# 5. Build and start
make prod-build
make prod-up

# 6. Verify health
curl https://yourdomain.com/health/
```

The `entrypoint.sh` script automatically runs `migrate` and `collectstatic` on every container start before the server comes up.

## Environment Variables

See `.env.example` for a fully documented list. The minimum required for production:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key — generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `ALLOWED_HOSTS` | Comma-separated list of your domain(s) |
| `POSTGRES_*` | Database credentials |
| `REDIS_URL` | Redis connection string |
| `AWS_ACCESS_KEY_ID` | S3 credentials for media storage |
| `AWS_SECRET_ACCESS_KEY` | S3 credentials |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket name |
| `EMAIL_HOST` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | SMTP for transactional email |

## Services

| Container | Role | Restart policy |
|---|---|---|
| `django` | Gunicorn + Uvicorn workers (ASGI) | `unless-stopped` |
| `celery` | Async task worker (image processing, emails) | `unless-stopped` |
| `celery-beat` | Periodic task scheduler (view/like count sync) | `unless-stopped` |
| `db` | PostgreSQL 17 | `unless-stopped` |
| `redis` | Cache, Celery broker, Channels layer | `unless-stopped` |
| `nginx` | TLS termination, static files, rate limiting | `unless-stopped` |

## SSL with Let's Encrypt

```bash
# Install certbot
apt install certbot

# Obtain certificate (stop nginx first if port 80 is in use)
certbot certonly --standalone -d yourdomain.com

# Certificates land at:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem

# Mount them into nginx (update docker-compose.prod.yml volumes)
```

Auto-renewal via cron:
```bash
echo "0 3 * * * certbot renew --quiet && docker compose -f /path/to/docker-compose.prod.yml restart nginx" | crontab -
```

## Database Backups

```bash
# Manual backup
docker compose exec db pg_dump -U pinboard pinboard | gzip > backup_$(date +%Y%m%d).sql.gz

# Restore
gunzip < backup_20260101.sql.gz | docker compose exec -T db psql -U pinboard pinboard

# Automated daily backup (add to crontab)
0 2 * * * docker compose -f /path/to/docker-compose.prod.yml exec -T db \
  pg_dump -U pinboard pinboard | gzip > /backups/pinboard_$(date +\%Y\%m\%d).sql.gz
```

## Scaling

### Horizontal web scaling

Increase Gunicorn workers in the Dockerfile CMD:
```
--workers 8 --worker-class uvicorn.workers.UvicornWorker
```

Or scale the Django container:
```bash
docker compose -f docker-compose.prod.yml up -d --scale django=3
```

nginx already uses `keepalive 32` upstream connections to handle multiple backends.

### Celery workers

```bash
# Scale task workers independently
docker compose -f docker-compose.prod.yml up -d --scale celery=4
```

Use separate queues for image processing vs. email delivery:
```bash
# In docker-compose.prod.yml celery command:
celery -A infrastructure.celery worker -Q images --concurrency=2
celery -A infrastructure.celery worker -Q default --concurrency=4
```

### Redis

For high traffic, move to Redis Cluster or use a managed service (AWS ElastiCache, Upstash). Update `REDIS_URL`, `CELERY_BROKER_URL`, and `CELERY_RESULT_BACKEND` to point to the cluster.

### PostgreSQL

Enable connection pooling with PgBouncer in front of PostgreSQL. `CONN_MAX_AGE=60` and `CONN_HEALTH_CHECKS=True` are already set in production settings.

For read-heavy workloads, add a replica and point `ImageSelector` queries at it using Django's database router.

## Observability

- **Logs**: All services log JSON to stdout (structlog in production). Collect with Loki, Datadog, or CloudWatch.
- **Health check**: `GET /health/` returns `{"status": "ok"}` — used by the nginx upstream health check and load balancer.
- **Metrics**: Add `django-prometheus` and scrape `/metrics/` with Prometheus for request latency, DB query counts, and Celery queue depth.
- **Errors**: Set `SENTRY_DSN` and add `sentry-sdk[django]` to capture exceptions in production.

## CI / CD

GitHub Actions runs lint + tests on every push. To add deployment:

```yaml
# .github/workflows/deploy.yml
on:
  push:
    branches: [master]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy via SSH
        run: |
          ssh user@yourserver "cd /app && git pull && make prod-build && make prod-up"
```
