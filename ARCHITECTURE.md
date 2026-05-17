# Architecture

## Overview

Pinboard is a social image bookmarking platform built with Django 5.2. The architecture follows a strict service/selector pattern — views are thin, all business logic lives in service classes, and all query logic lives in selector classes.

```
Request → View → Service → Model
                ↓
           Selector (reads)
```

## Directory Structure

```
pinboard/
├── config/                  # Django settings (base / development / testing / production)
├── apps/
│   ├── accounts/            # User, Profile, Follow, Block — auth and social graph
│   ├── images/              # Image, Collection, Like, Save — core product
│   ├── activity/            # Activity stream (actor + verb + target)
│   ├── notifications/       # In-app notifications + WebSocket push
│   ├── search/              # PostgreSQL full-text search
│   └── moderation/          # Report system
├── api/
│   └── v1/                  # Django Ninja REST API with JWT auth
├── shared/
│   ├── models/              # BaseModel = UUID + timestamps + soft delete
│   ├── exceptions.py        # Typed application exceptions
│   ├── cache.py             # Namespaced Redis cache keys
│   ├── pagination.py        # Reusable paginator
│   └── utils/               # Image processing, slugify helpers
├── infrastructure/
│   ├── celery.py            # Celery app + beat schedule
│   └── storage.py           # S3 storage backend
├── templates/
│   ├── base.html            # TailwindCSS CDN, HTMX, Alpine.js, WebSocket client
│   ├── components/          # Reusable partials (image_card, follow_button, etc.)
│   └── pages/               # Full page templates per feature
├── tests/
│   ├── factories/           # factory_boy factories for all models
│   ├── unit/                # Service-layer unit tests
│   ├── integration/         # View-layer integration tests
│   └── api/                 # Ninja API endpoint tests
└── docker/
    ├── django/              # Dockerfile + entrypoint.sh
    └── nginx/               # nginx.conf (TLS, rate limiting, WebSocket proxy)
```

## Key Architectural Decisions

### Service / Selector Pattern

All write operations go through a `*Service` class. All read queries go through a `*Selector` class. Views never construct querysets directly.

```python
# Good
images = ImageSelector.following_feed(user=request.user)
EngagementService.like(user=request.user, image_id=image_id)

# Never in views
Image.objects.filter(owner=request.user, status="ready")
```

### BaseModel

Every domain model inherits from `BaseModel`:

```python
class BaseModel(UUIDModel, TimestampedModel, SoftDeleteModel):
    pass
```

- **UUIDModel** — `id` is a UUID primary key (no sequential integer enumeration)
- **TimestampedModel** — `created_at`, `updated_at` on every record
- **SoftDeleteModel** — `deleted_at` field; `objects` excludes soft-deleted, `all_objects` includes them

### taggit UUID fix

`django-taggit` assumes integer PKs by default. Images use UUID PKs, so a custom through model is required:

```python
class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    class Meta:
        verbose_name = "Tag"
```

### Async side-effects via `transaction.on_commit`

Notifications, activity recording, and Celery task dispatch all happen **after** the transaction commits. This avoids holding DB locks while dispatching to Redis/Celery:

```python
transaction.on_commit(lambda: _post_like(user, image))
```

### Redis usage

| Purpose | Key pattern | TTL |
|---|---|---|
| View counts | `image:views:{id}` | None (flushed to DB by beat task) |
| Like counts | `image:likes:{id}` | None |
| User feed cache | `feed:{user_id}` | 300s |

### WebSocket notifications

Django Channels + channels-redis. Each authenticated user joins group `notifications_{user_id}` on connect. `NotificationService.send()` calls `group_send()` synchronously via `async_to_sync`. The browser JS reconnects automatically on close.

### Image processing pipeline

```
Upload/Bookmark → Image(status=pending) → process_image_task (Celery)
    → compress to WebP (max 2048px) → generate thumbnail (400×400)
    → Image(status=ready)
```

## Data Model

```
User ─── Profile (1:1)
     ├── Follow (M:M self)
     ├── Block  (M:M self)
     ├── Image ─── Like   (M:M User)
     │         ├── Save   (M:M User)
     │         ├── Collection (FK)
     │         └── UUIDTaggedItem → Tag
     ├── Activity (actor + verb + target GenericFK)
     ├── Notification (recipient + actor + verb + target GenericFK)
     └── Report (reporter + target GenericFK)
```

## API

Django Ninja REST API at `/api/v1/`. JWT authentication via `Authorization: Bearer <token>`.

Interactive docs: **`/api/v1/docs`**

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/accounts/register/` | — | Register + get tokens |
| POST | `/api/v1/accounts/login/` | — | Login + get tokens |
| POST | `/api/v1/accounts/follow/{id}/` | JWT | Follow a user |
| DELETE | `/api/v1/accounts/follow/{id}/` | JWT | Unfollow |
| GET | `/api/v1/images/feed/` | JWT | Paginated following feed |
| GET | `/api/v1/images/trending/` | — | Trending images |
| POST | `/api/v1/images/bookmark/` | JWT | Bookmark image from URL |
| POST | `/api/v1/images/{id}/like/` | JWT | Like an image |
| DELETE | `/api/v1/images/{id}/like/` | JWT | Unlike |
| POST | `/api/v1/images/{id}/view/` | — | Record a view |

## Performance Considerations

- All list views use `select_related` + `prefetch_related` to avoid N+1 queries
- HTMX infinite scroll fetches subsequent pages as partials — no full page reload
- View counts are incremented in Redis and flushed to PostgreSQL every 10 minutes by Celery beat — no write-per-request to the DB
- Feed queries are cached per-user for 5 minutes in Redis; cache is invalidated on follow/unfollow
- PostgreSQL indexes on every `status`, `privacy`, `created_at`, `like_count`, `view_count` column used for sorting/filtering

## Security

- CSRF protection on all state-changing endpoints
- Rate limiting: 10 register/hour, 20 login/hour per IP (django-ratelimit); nginx adds a second layer
- All file uploads validated by Pillow before processing
- Soft deletes preserve audit trail
- All UUIDs — no enumerable integer IDs exposed in URLs
- JWT tokens for the API with short access TTL (60min) and rotating refresh tokens
