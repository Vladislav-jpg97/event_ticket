# 🎟️ Event Ticketing Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/FastAPI-async-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Redis-cache%20%7C%20locks%20%7C%20broker-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis" />
  <img src="https://img.shields.io/badge/Celery-background%20jobs-37814A?style=for-the-badge&logo=celery&logoColor=white" alt="Celery" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0%20async-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy 2.0" />
  <img src="https://img.shields.io/badge/Alembic-migrations-6BA539?style=flat-square" alt="Alembic" />
  <img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white" alt="Pydantic v2" />
  <img src="https://img.shields.io/badge/JWT-access%20%2B%20refresh-000000?style=flat-square&logo=jsonwebtokens&logoColor=white" alt="JWT" />
  <img src="https://img.shields.io/badge/QR-qrcode-black?style=flat-square" alt="QR Code" />
  <img src="https://img.shields.io/badge/status-in%20development-yellow?style=flat-square" alt="Status" />
  <img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License" />
</p>

<p align="center">
  A REST API for an event ticketing platform — organizers publish events, attendees
  discover and buy tickets, and the system guarantees you can never oversell a venue.
  Built as a team learning project modeled on a real client engagement.
</p>

---

## 📖 About the Project

**Client:** Sanzhar Mirzaev, founder of the event agency **"Vivid Events"** (Tashkent, Uzbekistan).

Vivid Events currently sells tickets manually — through Instagram DMs and a spreadsheet —
which has already led to overselling a venue (312 tickets sold for a 300-seat show). This
platform replaces that process with a real ticketing backend: registration, event
management, ticket purchasing with **race-condition-safe seat allocation**, QR-code
check-in, email notifications, reviews, and search.

> This is a training project run like a real engagement: a discovery call, a written
> spec, an open-questions list, and a two-person team splitting the backlog by epic.

### Core guarantees the client asked for

1. Anyone can register as an **organizer** or an **attendee**
2. Organizers can create, publish, and cancel events
3. Attendees can search/filter events and buy 1–5 tickets at a time
4. **Selling more tickets than available seats must be impossible**, even under concurrent purchases
5. Buyers get an email confirmation with a **QR code** for entry
6. Cancelled events notify every buyer automatically
7. Attendees can review events they actually attended

---

## 🧭 Table of Contents

- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Domain Model (ER Diagram)](#-domain-model-er-diagram)
- [State Machines](#-state-machines)
- [Concurrency: How Overselling Is Prevented](#-concurrency-how-overselling-is-prevented)
- [Project Structure](#-project-structure)
- [Getting Started — Step by Step](#-getting-started--step-by-step)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Redis Keys](#-redis-keys)
- [Celery Tasks](#-celery-tasks)
- [Error Format](#-error-format)
- [Team & Task Breakdown (Who Does What)](#-team--task-breakdown-who-does-what)
- [Git Workflow](#-git-workflow)
- [Open Questions / Assumptions](#-open-questions--assumptions)
- [Definition of Done](#-definition-of-done)

---

## 🛠 Tech Stack

| Layer | Technology |
| --- | --- |
| Web framework | FastAPI (async) + Uvicorn |
| Database | PostgreSQL + SQLAlchemy 2.0 (async, `Mapped`/`mapped_column`) |
| Migrations | Alembic (async engine) |
| Validation | Pydantic v2 + `pydantic-settings` |
| Cache / locks / counters | Redis (`redis[hiredis]`) |
| Background jobs | Celery + Redis broker, Celery Beat for schedules |
| Auth | JWT (`python-jose`) + `passlib[bcrypt]` |
| Email | `aiosmtplib` |
| QR codes | `qrcode[pil]` |
| Slugs | `python-slugify` |
| File uploads | `python-multipart` |

---

## 🏗 Architecture

Layered architecture, same pattern across every domain (Auth, Events, Tickets, Reviews):

```
Router (app/api/v1/*.py)
   │   parses request, applies auth dependencies, sets status codes
   ▼
Service (app/services/*.py)
   │   business rules: slug generation, state machine transitions,
   │   Redis seat locking, cache invalidation, permission checks
   ▼
Repository (app/repositories/*.py)
   │   SQL only — extends a generic BaseRepository[T] with CRUD
   ▼
Model (app/models/*.py)
       SQLAlchemy ORM models
```

Supporting infrastructure sits alongside this stack:

- **Redis** — JWT blacklist, rate limiting, seat counters (race-condition guard),
  view counters, short-lived tokens (email verification / password reset), popular-events cache.
- **Celery + Celery Beat** — all outbound email is asynchronous; a separate worker process
  sends confirmations/reminders/digests so the API never blocks on SMTP.

---

## 🗺 Domain Model (ER Diagram)

```mermaid
erDiagram
    USER ||--o{ EVENT : "organizes"
    USER ||--o{ TICKET : "buys"
    USER ||--o{ REVIEW : "writes"
    EVENT ||--o{ TICKET : "has"
    EVENT ||--o{ REVIEW : "receives"
    EVENT }o--|| CATEGORY : "belongs to"
    EVENT }o--o{ TAG : "tagged with"

    USER {
        int id PK
        string email
        string username
        string hashed_password
        enum role
        bool is_verified
        bool is_active
        string bio
        string avatar_url
    }

    EVENT {
        int id PK
        string title
        string slug
        text description
        string venue
        string city
        datetime starts_at
        datetime ends_at
        int capacity
        decimal price
        enum status
        int organizer_id FK
        int category_id FK
    }

    TICKET {
        int id PK
        string uuid
        int event_id FK
        int buyer_id FK
        int quantity
        decimal total_price
        enum status
    }

    REVIEW {
        int id PK
        int event_id FK
        int author_id FK
        int rating
        text comment
    }

    CATEGORY {
        int id PK
        string name
        string slug
    }

    TAG {
        int id PK
        string name
    }
```

Full field-level definitions (types, constraints, nullability) live in the technical
spec, Section 3.1 — keep the ORM models in sync with that table.

---

## 🔄 State Machines

**Event lifecycle**

```
draft ──publish──→ published ──complete──→ completed
  ↑                    │
  └──────────────── cancel ──→ cancelled
```

**Ticket lifecycle**

```
pending ──pay──→ paid ──cancel──→ cancelled
                          (only allowed 2h+ before the event starts)
```

Invalid transitions (e.g. publishing an already-cancelled event) must return `400`
with a message naming the disallowed transition — implement this as a small
`TRANSITIONS` mapping checked in the service layer, not scattered `if` statements.

---

## ⚔️ Concurrency: How Overselling Is Prevented

This is the hardest and most important piece of the whole project (`TKT-002`).

**The problem:** two buyers both see "3 seats left" and both try to buy 3 tickets.
If the availability check happens against Postgres with a plain `SELECT` + `INSERT`,
both requests can pass the check before either commits — the venue oversells.

**The fix:** seat counts live in Redis, not just Postgres, and are decremented
**atomically** via a Lua script (`EVAL`) before any database write happens. Redis is
single-threaded, so two simultaneous `EVAL` calls are automatically serialized —
only one of them can be the one that takes the last seats.

```
1. Publish event  → SET event:seats:{event_id} = capacity   (no TTL)

2. Purchase request:
   a. EVAL lua_script  → atomically checks & decrements seats
      → not enough seats → 409, no DB row created
      → enough seats     → seats reserved
   b. INSERT Ticket (status = pending)
   c. Run mock payment
      → fails  → INCR seats back, delete Ticket → 402
      → succeeds → UPDATE Ticket SET status = paid
   d. Celery: send_ticket_confirmation.delay(ticket_id)

3. Cancel ticket (2h+ before event) → INCRBY seats back, ticket → cancelled
```

`total_price` is captured on the ticket at purchase time — it must never be
recalculated from the event's current price later.

---

## 📁 Project Structure

```text
event-ticketing/
├── app/
│   ├── main.py                     # app factory, lifespan, middleware, routers
│   ├── config.py                   # Settings (pydantic-settings)
│   ├── database.py                 # async engine, sessionmaker, get_db
│   │
│   ├── core/
│   │   ├── security.py             # hash/verify password, JWT create/decode
│   │   ├── redis.py                # get_redis dependency
│   │   └── celery.py               # Celery app + beat schedule
│   │
│   ├── models/
│   │   ├── mixins.py                # TimestampMixin
│   │   ├── user.py
│   │   ├── category.py / tag.py
│   │   ├── event.py
│   │   ├── ticket.py
│   │   └── review.py
│   │
│   ├── repositories/
│   │   ├── base.py                  # generic BaseRepository[T]
│   │   ├── user_repo.py
│   │   ├── event_repo.py
│   │   ├── ticket_repo.py
│   │   └── review_repo.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── event_service.py         # publish/cancel FSM, slug uniqueness
│   │   ├── ticket_service.py        # Redis seat locking, mock payment
│   │   └── review_service.py
│   │
│   ├── schemas/                     # Pydantic request/response models
│   ├── dependencies/
│   │   └── auth.py                  # get_current_user, require_role, require_verified
│   │
│   ├── api/v1/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── events.py
│   │   ├── tickets.py
│   │   ├── reviews.py
│   │   └── categories.py
│   │
│   └── tasks/                       # Celery tasks (email, reminders, digest)
│
├── alembic/                          # async-aware migrations
├── static/avatars/                   # uploaded avatar images
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started — Step by Step

### Prerequisites

- Python 3.12+
- PostgreSQL 14+ running locally (or in Docker)
- Redis 6+ running locally (or in Docker)
- An SMTP account for sending real email (Gmail App Password or Mailtrap both work)

### 1. Clone the repository

```bash
git clone https://github.com/<your-org>/event-ticketing.git
cd event-ticketing
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in at minimum: `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`
(32+ random characters), and your SMTP credentials. See the
[Environment Variables](#-environment-variables) table below for the full list.

### 4. Start PostgreSQL & Redis

If you don't already have them running locally:

```bash
docker run -d --name ticketing_postgres -p 5432:5432 \
  -e POSTGRES_USER=ticketing -e POSTGRES_PASSWORD=ticketing -e POSTGRES_DB=ticketing \
  postgres:16-alpine

docker run -d --name ticketing_redis -p 6379:6379 redis:7-alpine
```

### 5. Apply database migrations

```bash
alembic upgrade head
```

### 6. Start the API

```bash
uvicorn app.main:app --reload
```

Visit **http://localhost:8000/docs** to confirm Swagger UI loads.

### 7. Start the Celery worker (separate terminal)

```bash
celery -A app.core.celery worker --loglevel=info
```

This process sends all outbound email (registration verification, ticket
confirmations, cancellations).

### 8. Start Celery Beat — the scheduler (separate terminal)

```bash
celery -A app.core.celery beat --loglevel=info
```

This process triggers the three scheduled jobs: hourly reminders, the 5-minute
view-counter flush, and the Monday digest.

### 9. Smoke-test the full flow

```bash
# 1. Register an organizer
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"organizer@test.com","username":"organizer1","password":"SecurePass123","role":"organizer"}'

# 2. Log in, grab the access token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"organizer@test.com","password":"SecurePass123"}'

# 3. Create + publish an event, register an attendee, buy tickets, etc.
#    (see /docs for the full request/response shapes)
```

You now have a running API, an async worker, and a scheduler — the three
processes this project always runs as.

---

## 🔐 Environment Variables

| Variable | Description |
| --- | --- |
| `APP_NAME` | Application display name |
| `DEBUG` | Debug mode (`true`/`false`) — also toggles SQL echo |
| `DATABASE_URL` | Async Postgres URL, e.g. `postgresql+asyncpg://user:pass@localhost/db` |
| `REDIS_URL` | Redis connection string |
| `SECRET_KEY` | JWT signing secret, 32+ characters |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL (spec default: 15) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL (spec default: 30) |
| `FRONTEND_URL` | Base URL used to build links inside emails |
| `SMTP_HOST` / `SMTP_PORT` | SMTP server address/port |
| `SMTP_USER` / `SMTP_PASSWORD` | SMTP credentials |
| `EMAILS_FROM` | "From" address on outgoing email |

Only `.env.example` is committed; `.env` is git-ignored.

---

## 📡 API Reference

Full interactive docs live at **`/docs`** once the app is running. Summary below.

### Auth — `/api/v1/auth`
| Method | Path | Access |
| --- | --- | :---: |
| POST | `/register` | Public |
| POST | `/login` | Public |
| POST | `/refresh` | Public (reads httponly cookie) |
| POST | `/logout` | Auth |
| POST | `/verify-email` | Public |
| POST | `/forgot-password` | Public |
| POST | `/reset-password` | Public |

### Users — `/api/v1/users`
| Method | Path | Access |
| --- | --- | :---: |
| GET | `/me` | Auth |
| PATCH | `/me` | Auth |
| POST | `/me/avatar` | Auth |
| GET | `/{username}` | Public |
| GET | `/{username}/events` | Public |

### Events — `/api/v1/events`
| Method | Path | Access |
| --- | --- | :---: |
| POST | `/` | Organizer |
| GET | `/` | Public (search/filter/sort, see below) |
| GET | `/popular` | Public (Redis-cached top 10) |
| GET | `/{slug}` | Public |
| PATCH | `/{slug}` | Organizer (owner), draft only |
| DELETE | `/{slug}` | Organizer (owner) / Admin, draft only |
| PATCH | `/{slug}/publish` | Organizer (owner) |
| PATCH | `/{slug}/cancel` | Organizer (owner) / Admin |
| GET | `/{slug}/stats` | Organizer (owner) |

**`GET /events` query params:** `q`, `category`, `tag`, `city`, `date_from`, `date_to`,
`price_min`, `price_max`, `sort` (`date_asc`/`date_desc`/`price_asc`/`price_desc`/`rating`/`popular`),
`page`, `size` (max 100).

### Tickets
| Method | Path | Access |
| --- | --- | :---: |
| POST | `/api/v1/events/{slug}/tickets` | Attendee |
| GET | `/api/v1/events/{slug}/tickets` | Auth (own tickets for that event) |
| DELETE | `/api/v1/events/{slug}/tickets/{ticket_id}` | Auth (owner) |
| GET | `/api/v1/tickets/my` | Auth |
| GET | `/api/v1/tickets/{ticket_id}/qr` | Auth (owner) — returns PNG |

### Reviews — `/api/v1/events/{slug}/reviews`
| Method | Path | Access |
| --- | --- | :---: |
| POST | `/` | Attendee who bought a ticket |
| GET | `/` | Public |
| DELETE | `/{review_id}` | Auth (owner) / Moderator |

### Categories & Tags
| Method | Path | Access |
| --- | --- | :---: |
| GET / POST | `/api/v1/categories` | Public / Admin |
| GET / POST | `/api/v1/tags` | Public / Admin |

---

## 🔑 Redis Keys

| Key | Value | TTL | Purpose |
| --- | --- | :---: | --- |
| `blacklist:{jti}` | `"1"` | remaining token life | Revoked access tokens (logout) |
| `verify:{token}` | `user_id` | 24h | Email verification |
| `reset:{token}` | `email` | 1h | Password reset |
| `login_attempts:{ip}` | count | 15 min | Login rate limiting |
| `global_rate:{ip}` | count | 60s | Global 100 req/min rate limit |
| `event:seats:{event_id}` | int | none | Available seats (race-condition guard) |
| `event:views:{event_id}` | int | none | View counter, flushed to DB every 5 min |
| `popular_events` | JSON | 5 min | Cached top-10 by views |

---

## ⏱ Celery Tasks

**Triggered by events:**
| Task | Trigger | Behavior |
| --- | --- | --- |
| `send_verification_email` | after register | verification link, retries on SMTP failure |
| `send_password_reset_email` | after forgot-password | reset link, retries on SMTP failure |
| `send_ticket_confirmation` | after successful payment | event details + QR PNG attachment, retries ×3 / 60s |
| `send_event_cancellation` | event → cancelled | batched email to every paid ticket holder |

**Scheduled (Celery Beat):**
| Task | Schedule | Behavior |
| --- | --- | --- |
| `send_event_reminders` | hourly | emails buyers of events starting in ~24h |
| `flush_view_counters` | every 5 min | moves `event:views:*` from Redis into the DB `views` column, then clears the keys |
| `send_weekly_digest` | Monday 9:00 | top-5 upcoming published events, sent to all active users |

---

## ⚠️ Error Format

Every error response, regardless of status code, follows one shape:

```json
{
  "error": "not_found",
  "message": "Event not found"
}
```

Validation errors (`422`) additionally include a `details` array:

```json
{
  "error": "validation_error",
  "message": "Invalid input data",
  "details": [
    { "field": "starts_at", "message": "Start date must be in the future" }
  ]
}
```

| `error` code | HTTP status | When |
| --- | :---: | --- |
| `unauthorized` | 401 | missing/expired/blacklisted token |
| `forbidden` | 403 | insufficient role or not the resource owner |
| `not_found` | 404 | resource doesn't exist |
| `conflict` | 409 | duplicate (email taken, no seats left) |
| `validation_error` | 422 | malformed input |
| `rate_limit_exceeded` | 429 | too many requests |
| `internal_error` | 500 | unhandled server error |

---

## 👥 Team & Task Breakdown (Who Does What)

Two-person team, split by epic. Full task-level detail (acceptance criteria,
technical notes, estimates) lives in the project backlog — this is the summary.

### S1 — Foundation, Auth, User, Middleware, Celery setup (~36–37.5h)

| Epic | Responsibility |
| --- | --- |
| **Project Foundation** | Repo/branch setup, `Settings`, async DB engine + `get_db`, Alembic init, Redis client, generic `BaseRepository[T]`, and the API-contract pass (Pydantic schemas + stub routers returning `501` for **every** endpoint in the spec, including S2's, so `/docs` and `/openapi.json` are complete on day one) |
| **Authentication** | `User` model, password hashing + JWT utils, register, login (with rate limiting), logout + token blacklist, refresh, email verification, password reset, and the shared `get_current_user` / `require_role` / `require_verified` dependencies that everything else depends on |
| **User Profile** | `GET/PATCH /users/me`, public profile, avatar upload |
| **Middleware & Security** | CORS, request logging, global exception handlers (unified error format), global rate-limit middleware |
| **Celery setup + core notifications** | `core/celery.py` + Beat schedule skeleton, verification email task, password-reset email task |

> **S1 owns the critical path.** `get_current_user` and the auth dependencies must
> land early — S2's Events/Tickets endpoints are blocked on them.

### S2 — Categories, Events, Tickets, Reviews, Search, Notifications (~44–46h)

| Epic | Responsibility |
| --- | --- |
| **Categories & Tags** | Models + association table, public GET / admin POST endpoints |
| **Events** | `Event` model, create (with slug generation + tag get-or-create), list with pagination, detail view with Redis view counter, update, publish/cancel state machine, popular-events cache, organizer sales stats |
| **Ticketing System** | `Ticket` model, **the race-condition-safe purchase flow** (the hardest task in the whole backlog), cancellation with the 2-hour cutoff, QR-code generation/serving, "my tickets" listing |
| **Reviews** | `Review` model with a unique `(event_id, author_id)` constraint, purchase-gated creation, list + average rating, deletion |
| **Search & Discovery** | Extends the Events list endpoint with full-text search (`ILIKE`), category/tag/city/date/price filters, and all sort modes |
| **Event-side notifications** | Ticket confirmation email (with QR attachment), event-cancellation broadcast, reminder + digest scheduled tasks |

### Suggested working order

1. **S1**: Foundation → Auth models/utils → `get_current_user` (unblocks S2)
2. **S2**: Categories/Tags → Event model & CRUD (in parallel with S1's auth work, once the API-contract stubs exist)
3. **S1**: remaining Auth endpoints, Middleware, Celery setup
4. **S2**: Ticket purchase flow (needs `get_current_user` + Celery from S1) → Reviews → Search
5. **Both**: Notifications wiring, then joint QA against the client's demo checklist

---

## 🌿 Git Workflow

**Branches**
```
main        — production-ready, no direct pushes, PR only
develop     — integration branch, everything merges here
feature/*   — e.g. feature/ticket-purchase
fix/*       — e.g. fix/race-condition-seats
chore/*     — deps, config, refactors
```

**Commits** — [Conventional Commits](https://www.conventionalcommits.org/):
```
feat(auth): add JWT refresh token endpoint
fix(tickets): return seats to Redis on payment failure
chore(deps): add qrcode and aiosmtplib packages
```

**Pull requests**
1. Branch off `develop`
2. Open a PR describing what changed and how to test it
3. At least one approval from the other teammate before merging
4. Author merges after approval, then deletes the branch

---

## ❓ Open Questions / Assumptions

The following weren't resolved with the client before development started. Decisions
made by the team in their absence are recorded here — update this table once real
answers come in.

| # | Question | Assumption made |
| --- | --- | --- |
| 1 | Can organizers create free events (`price = 0`)? | *fill in* |
| 2 | Is event moderation required before publishing? | *fill in* |
| 3 | Can capacity be reduced after tickets are sold? | *fill in* |
| 4 | Multiple ticket tiers per event (VIP/Standard)? | *fill in* |
| 5 | Can organizers see buyer contact info? | *fill in* |
| 6 | Automatic refund on event cancellation, or manual? | *fill in* |
| 7 | Age restrictions (18+) on some events? | *fill in* |
| 8 | Search by organizer name? | *fill in* |

---

## ✅ Definition of Done

- [ ] All endpoints documented in Swagger (`/docs`)
- [ ] Buying the last ticket from two concurrent requests is handled correctly (no oversell)
- [ ] Email notifications are sent asynchronously via Celery, never inline in a request
- [ ] Every error response follows the unified format
- [ ] Code is separated into router → service → repository layers throughout
- [ ] `.env.example` present, `.env` git-ignored
- [ ] `alembic upgrade head` runs cleanly from an empty database
- [ ] All three roles (attendee, organizer, admin) manually verified via Swagger/Postman
- [ ] Open questions above are filled in with the team's actual assumptions

---

<p align="center">
  <sub>Built as a two-person team project — from a client discovery call to a race-condition-safe ticket purchase flow.</sub>
</p>