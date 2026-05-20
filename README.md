<div align="center">

# Pinboard

**A social image bookmarking platform — discover, save, and share the images that inspire you.**

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=flat-square&logo=django&logoColor=white)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

</div>

---

## What is Pinboard?

Pinboard is a full-stack social image bookmarking platform built with **Django 5.2**. Users can upload or bookmark images from any URL, organise them into collections, follow other creators, like and save content, and get real-time notifications — all through a fast, dark-themed UI powered by HTMX and Alpine.js with no heavy JavaScript framework.

---

## Features

| Category | Highlights |
|---|---|
| **Auth** | Email-based signup, Google & GitHub OAuth, JWT API tokens, password reset via email, rate-limited login |
| **Images** | Upload files or bookmark from URL, automatic WebP conversion, thumbnail generation, full-text search |
| **Social** | Follow / unfollow, block users, activity feed, real-time WebSocket notifications |
| **Collections** | Organise images into named collections (public or private) |
| **Engagement** | Like, save, view counts — Redis-backed with periodic DB sync via Celery beat |
| **API** | Full REST API at `/api/v1/` with interactive Swagger docs |
| **Admin** | Django admin with moderation report review, bulk resolve/dismiss actions |
| **Performance** | HTMX infinite scroll, Redis feed cache, `select_related` / `prefetch_related` on all list views, GIN-indexed FTS |

---

## Tech Stack

```
Backend       Django 5.2 · Django Ninja (REST API) · Celery · Django Channels (WebSockets)
Database      PostgreSQL 17 · django-redis cache
Storage       Local dev / AWS S3 (or Cloudflare R2) in production
Auth          Custom UUID User model · Social Auth (Google, GitHub) · SimpleJWT
Frontend      HTMX · Alpine.js · TailwindCSS (dark theme)
Infrastructure Docker Compose · Gunicorn + Uvicorn (ASGI) · Nginx · Celery Beat
Testing       pytest · factory_boy · 76 tests at 65% coverage
```

---

## Quick Start

### Prerequisites
- Docker 24+ and Docker Compose v2
- Git

### Run locally in 3 steps

```bash
# 1. Clone the repo
git clone https://github.com/elsayed07/Pinboard.git
cd Pinboard

# 2. Copy environment config and start containers
cp .env.example .env
docker compose up --build -d

# 3. Seed sample data (downloads 8 real images)
docker compose exec django uv run python manage.py seed
```

Visit **http://localhost:8000** — the app is live.

> **Default seed credentials** — each seeded user has the password `Test1234!`.
> The seed creates accounts for Apple, Microsoft, Tesla, Amazon, NVIDIA, Alphabet, Meta, and a superuser.

### Useful commands

```bash
# Run the test suite
docker compose exec django uv run pytest tests/ -q

# Apply migrations
docker compose exec django uv run python manage.py migrate

# Open a Django shell
docker compose exec django uv run python manage.py shell

# Rebuild search index for existing images
docker compose exec django uv run python manage.py update_search_vectors

# Tail logs
docker compose logs -f django
```

---

## Project Structure

```
pinboard/
├── apps/
│   ├── accounts/       # Users, profiles, follow graph, block list
│   ├── images/         # Images, collections, likes, saves, tags
│   ├── activity/       # Activity feed (actor + verb + target)
│   ├── notifications/  # In-app notifications + WebSocket push
│   ├── search/         # PostgreSQL full-text search
│   └── moderation/     # Content report system
├── api/v1/             # Django Ninja REST API (JWT)
├── config/             # Django settings (base / development / production)
├── infrastructure/     # Celery app + beat schedule, S3 storage backend
├── shared/             # BaseModel, typed exceptions, cache keys, pagination
├── templates/          # HTMX-powered templates (base, pages, components)
├── tests/              # Unit, integration, and API test suites
└── docker/             # Dockerfiles, nginx config, entrypoint script
```

---

## Architecture

All business logic is organised around a **service / selector pattern** — views are thin HTTP adapters, services own write operations, and selectors own read queries. Views never construct querysets directly.

```
Request → View → Service → Model
                ↓
           Selector (reads)
```

Every domain model inherits from `BaseModel`:
- **UUID primary key** — no sequential integer enumeration in URLs
- **Timestamps** — `created_at` / `updated_at` on every row
- **Soft delete** — `deleted_at`; default manager excludes deleted records

Async side-effects (notifications, activity recording, Celery task dispatch) always happen inside `transaction.on_commit()` to avoid holding locks while writing to Redis or Celery.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for a deeper walkthrough and the full data model diagram.

---

## API

The REST API lives at `/api/v1/` with interactive Swagger docs at **`/api/v1/docs`**.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/accounts/register/` | — | Register + receive JWT tokens |
| `POST` | `/api/v1/accounts/login/` | — | Login + receive JWT tokens |
| `POST` | `/api/v1/accounts/follow/{id}/` | JWT | Follow a user |
| `DELETE` | `/api/v1/accounts/follow/{id}/` | JWT | Unfollow |
| `GET` | `/api/v1/images/feed/` | JWT | Paginated following feed |
| `GET` | `/api/v1/images/trending/` | — | Trending images |
| `POST` | `/api/v1/images/bookmark/` | JWT | Bookmark image from URL |
| `POST` | `/api/v1/images/{id}/like/` | JWT | Like an image |
| `DELETE` | `/api/v1/images/{id}/like/` | JWT | Unlike |
| `POST` | `/api/v1/images/{id}/view/` | — | Record a view |

---

## Production Deployment

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for the full guide covering:
- SSL with Let's Encrypt + auto-renewal
- Environment variables reference
- Horizontal scaling (Gunicorn workers, Celery queues)
- PostgreSQL backups and PgBouncer connection pooling
- Observability (structured JSON logs, Prometheus metrics, Sentry)

Quick production start:

```bash
cp .env.example .env          # fill in SECRET_KEY, DB, AWS, SMTP
make prod-build
make prod-up
curl https://yourdomain.com/health/
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `ALLOWED_HOSTS` | Comma-separated domain list |
| `POSTGRES_*` | Database credentials |
| `REDIS_URL` | Redis connection string |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_STORAGE_BUCKET_NAME` | S3 media storage |
| `EMAIL_HOST` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | SMTP for transactional email |
| `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY` / `_SECRET` | Google OAuth2 |
| `SOCIAL_AUTH_GITHUB_KEY` / `_SECRET` | GitHub OAuth2 |

See `.env.example` for the full documented list.

---



---

## License

MIT — see [LICENSE](LICENSE) for details.
