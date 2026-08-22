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
  REST API платформы для продажи билетов на мероприятия — организаторы публикуют события,
  покупатели находят их и покупают билеты, а система гарантирует, что зал никогда
  не будет продан «в минус». Командный учебный проект, смоделированный по мотивам
  реального клиентского запроса.
</p>

---

## 📖 О проекте

**Event Ticketing Platform** — REST API для продажи билетов на мероприятия.
Организаторы создают и публикуют события, покупатели ищут их, покупают билеты
и получают email с подтверждением и QR-кодом для входа. Система гарантирует, что
зал никогда не будет продан «в минус», даже при одновременных покупках.

Учебный командный проект: с письменным ТЗ, списком открытых вопросов и командой
из двух человек, разделившей бэклог по эпикам.

### Ключевые требования

1. Любой может зарегистрироваться как **организатор** или **покупатель**
2. Организаторы создают, публикуют и отменяют мероприятия
3. Покупатели ищут события и покупают от 1 до 5 билетов за раз
4. **Продать больше билетов, чем есть мест, — невозможно**, даже при одновременных покупках
5. Покупателю приходит письмо с подтверждением и **QR-кодом** для входа
6. Отмена мероприятия автоматически уведомляет всех покупателей
7. Отзыв можно оставить только если реально посетил мероприятие

---

## 🧭 Содержание

- [Стек технологий](#-стек-технологий)
- [Архитектура](#-архитектура)
- [Модель данных (ER-диаграмма)](#-модель-данных-er-диаграмма)
- [Машины состояний](#-машины-состояний)
- [Конкурентность: как предотвращается перепродажа мест](#-конкурентность-как-предотвращается-перепродажа-мест)
- [Структура проекта](#-структура-проекта)
- [Быстрый старт — пошагово](#-быстрый-старт--пошагово)
- [Переменные окружения](#-переменные-окружения)
- [Справочник API](#-справочник-api)
- [Ключи Redis](#-ключи-redis)
- [Задачи Celery](#-задачи-celery)
- [Формат ошибок](#-формат-ошибок)
- [Команда и распределение задач (кто что делает)](#-команда-и-распределение-задач-кто-что-делает)
- [Git Workflow](#-git-workflow)
- [Открытые вопросы / допущения](#-открытые-вопросы--допущения)
- [Критерии готовности (Definition of Done)](#-критерии-готовности-definition-of-done)

---

## 🛠 Стек технологий

| Слой | Технология |
| --- | --- |
| Веб-фреймворк | FastAPI (async) + Uvicorn |
| База данных | PostgreSQL + SQLAlchemy 2.0 (async, `Mapped`/`mapped_column`) |
| Миграции | Alembic (async engine) |
| Валидация | Pydantic v2 + `pydantic-settings` |
| Кэш / блокировки / счётчики | Redis (`redis[hiredis]`) |
| Фоновые задачи | Celery + Redis broker, Celery Beat для расписаний |
| Авторизация | JWT (`python-jose`) + `passlib[bcrypt]` |
| Email | `aiosmtplib` |
| QR-коды | `qrcode[pil]` |
| Slug | `python-slugify` |
| Загрузка файлов | `python-multipart` |

---

## 🏗 Архитектура

Слоистая архитектура, единая для всех доменов (Auth, Events, Tickets, Reviews):

```
Router (app/api/v1/*.py)
   │   разбирает запрос, применяет auth-зависимости, выставляет статус-коды
   ▼
Service (app/services/*.py)
   │   бизнес-логика: генерация slug, переходы машины состояний,
   │   блокировка мест в Redis, инвалидация кэша, проверка прав
   ▼
Repository (app/repositories/*.py)
   │   только SQL — наследуется от generic BaseRepository[T] с CRUD
   ▼
Model (app/models/*.py)
       SQLAlchemy ORM модели
```

Инфраструктура вокруг этого стека:

- **Redis** — blacklist JWT, rate limiting, счётчики мест (защита от race condition),
  счётчики просмотров, короткоживущие токены (верификация email / сброс пароля),
  кэш популярных событий.
- **Celery + Celery Beat** — вся исходящая почта асинхронна: отдельный воркер
  отправляет подтверждения/напоминания/дайджесты, чтобы API никогда не блокировался на SMTP.

---

## 🗺 Модель данных (ER-диаграмма)

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

Полное описание полей (типы, ограничения, nullable) — в техническом задании,
раздел 3.1. Держите ORM-модели синхронными с этой таблицей.

---

## 🔄 Машины состояний

**Жизненный цикл мероприятия**

```
draft ──publish──→ published ──complete──→ completed
  ↑                    │
  └──────────────── cancel ──→ cancelled
```

**Жизненный цикл билета**

```
pending ──pay──→ paid ──cancel──→ cancelled
                          (отмена разрешена только за 2ч+ до начала события)
```

Недопустимые переходы (например, публикация уже отменённого события) должны
возвращать `400` с сообщением о том, какой именно переход невозможен —
реализуйте это через небольшой словарь `TRANSITIONS` в сервисном слое,
а не через разбросанные `if`.

---

## ⚔️ Конкурентность: как предотвращается перепродажа мест

Это самая сложная и самая важная часть всего проекта (`TKT-002`).

**Проблема:** два покупателя одновременно видят «осталось 3 места» и оба пытаются
купить 3 билета. Если проверка доступности идёт обычным `SELECT` + `INSERT` в
Postgres, оба запроса могут пройти проверку до того, как любой из них закоммитится —
зал будет продан в минус.

**Решение:** количество мест хранится в Redis, а не только в Postgres, и
списывается **атомарно** через Lua-скрипт (`EVAL`) до любой записи в базу данных.
Redis однопоточный, поэтому два одновременных вызова `EVAL` автоматически
выполняются последовательно — только один из них может забрать последние места.

```
1. Публикация события  → SET event:seats:{event_id} = capacity   (без TTL)

2. Запрос на покупку:
   a. EVAL lua_script  → атомарно проверяет и списывает места
      → мест не хватает → 409, запись в БД не создаётся
      → мест хватило    → места зарезервированы
   b. INSERT Ticket (status = pending)
   c. Mock-оплата
      → упала    → INCR мест обратно, удалить Ticket → 402
      → успешна  → UPDATE Ticket SET status = paid
   d. Celery: send_ticket_confirmation.delay(ticket_id)

3. Отмена билета (за 2ч+ до события) → INCRBY мест обратно, билет → cancelled
```

`total_price` фиксируется на билете в момент покупки — его нельзя пересчитывать
позже по текущей цене события.

---

## 📁 Структура проекта

```text
event-ticketing/
├── app/
│   ├── main.py                     # фабрика приложения, lifespan, middleware, роутеры
│   ├── config.py                   # Settings (pydantic-settings)
│   ├── database.py                 # async engine, sessionmaker, get_db
│   │
│   ├── core/
│   │   ├── security.py             # хеширование пароля, создание/декодирование JWT
│   │   ├── redis.py                # DI-зависимость get_redis
│   │   └── celery.py               # приложение Celery + beat schedule
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
│   │   ├── event_service.py         # FSM publish/cancel, уникальность slug
│   │   ├── ticket_service.py        # блокировка мест в Redis, mock-оплата
│   │   └── review_service.py
│   │
│   ├── schemas/                     # Pydantic-схемы запросов/ответов
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
│   └── tasks/                       # задачи Celery (email, напоминания, дайджест)
│
├── alembic/                          # async-миграции
├── static/avatars/                   # загруженные аватары
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🚀 Быстрый старт — пошагово

### Требования

- Python 3.12+
- PostgreSQL 14+ (локально или в Docker)
- Redis 6+ (локально или в Docker)
- SMTP-аккаунт для реальной отправки писем (Gmail App Password или Mailtrap подойдут)

### 1. Склонировать репозиторий

```bash
git clone https://github.com/<your-org>/event-ticketing.git
cd event-ticketing
```

### 2. Создать виртуальное окружение и установить зависимости

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Настроить переменные окружения

```bash
cp .env.example .env
```

Открой `.env` и заполни как минимум: `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`
(32+ случайных символа) и данные SMTP. Полный список — в таблице
[Переменные окружения](#-переменные-окружения) ниже.

### 4. Запустить PostgreSQL и Redis

Если их ещё нет локально:

```bash
docker run -d --name ticketing_postgres -p 5432:5432 \
  -e POSTGRES_USER=ticketing -e POSTGRES_PASSWORD=ticketing -e POSTGRES_DB=ticketing \
  postgres:16-alpine

docker run -d --name ticketing_redis -p 6379:6379 redis:7-alpine
```

### 5. Применить миграции базы данных

```bash
alembic upgrade head
```

### 6. Запустить API

```bash
uvicorn app.main:app --reload
```

Открой **http://localhost:8000/docs** — должен загрузиться Swagger UI.

### 7. Запустить Celery worker (в отдельном терминале)

```bash
celery -A app.core.celery worker --loglevel=info
```

Этот процесс отправляет всю исходящую почту (верификация регистрации,
подтверждения билетов, уведомления об отмене).

### 8. Запустить Celery Beat — планировщик (в отдельном терминале)

```bash
celery -A app.core.celery beat --loglevel=info
```

Этот процесс запускает три задачи по расписанию: ежечасные напоминания,
flush счётчиков просмотров каждые 5 минут и дайджест по понедельникам.

### 9. Проверить полный флоу вручную

```bash
# 1. Зарегистрировать организатора
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"organizer@test.com","username":"organizer1","password":"SecurePass123","role":"organizer"}'

# 2. Залогиниться, получить access token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"organizer@test.com","password":"SecurePass123"}'

# 3. Создать и опубликовать событие, зарегистрировать покупателя, купить билеты и т.д.
#    (полные форматы запросов/ответов — в /docs)
```

Теперь у тебя запущены три процесса, на которых всегда держится этот проект:
API, асинхронный воркер и планировщик.

---

## 🔐 Переменные окружения

| Переменная | Описание |
| --- | --- |
| `APP_NAME` | Название приложения |
| `DEBUG` | Режим отладки (`true`/`false`) — также включает SQL echo |
| `DATABASE_URL` | Async-строка подключения к Postgres, напр. `postgresql+asyncpg://user:pass@localhost/db` |
| `REDIS_URL` | Строка подключения к Redis |
| `SECRET_KEY` | Секретный ключ подписи JWT, 32+ символа |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни access token (по ТЗ — 15) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Время жизни refresh token (по ТЗ — 30) |
| `FRONTEND_URL` | Базовый URL для ссылок в письмах |
| `SMTP_HOST` / `SMTP_PORT` | Адрес/порт SMTP-сервера |
| `SMTP_USER` / `SMTP_PASSWORD` | Учётные данные SMTP |
| `EMAILS_FROM` | Адрес отправителя в письмах |

В репозитории коммитится только `.env.example`; `.env` — в `.gitignore`.

---

## 📡 Справочник API

Полная интерактивная документация доступна на **`/docs`** после запуска приложения.
Ниже — краткая сводка.

### Auth — `/api/v1/auth`
| Метод | Путь | Доступ |
| --- | --- | :---: |
| POST | `/register` | Public |
| POST | `/login` | Public |
| POST | `/refresh` | Public (читает httponly cookie) |
| POST | `/logout` | Auth |
| POST | `/verify-email` | Public |
| POST | `/forgot-password` | Public |
| POST | `/reset-password` | Public |

### Users — `/api/v1/users`
| Метод | Путь | Доступ |
| --- | --- | :---: |
| GET | `/me` | Auth |
| PATCH | `/me` | Auth |
| POST | `/me/avatar` | Auth |
| GET | `/{username}` | Public |
| GET | `/{username}/events` | Public |

### Events — `/api/v1/events`
| Метод | Путь | Доступ |
| --- | --- | :---: |
| POST | `/` | Organizer |
| GET | `/` | Public (поиск/фильтры/сортировка, см. ниже) |
| GET | `/popular` | Public (кэш топ-10 в Redis) |
| GET | `/{slug}` | Public |
| PATCH | `/{slug}` | Organizer (владелец), только draft |
| DELETE | `/{slug}` | Organizer (владелец) / Admin, только draft |
| PATCH | `/{slug}/publish` | Organizer (владелец) |
| PATCH | `/{slug}/cancel` | Organizer (владелец) / Admin |
| GET | `/{slug}/stats` | Organizer (владелец) |

**Query-параметры `GET /events`:** `q`, `category`, `tag`, `city`, `date_from`,
`date_to`, `price_min`, `price_max`, `sort` (`date_asc`/`date_desc`/`price_asc`/
`price_desc`/`rating`/`popular`), `page`, `size` (максимум 100).

### Tickets
| Метод | Путь | Доступ |
| --- | --- | :---: |
| POST | `/api/v1/events/{slug}/tickets` | Attendee |
| GET | `/api/v1/events/{slug}/tickets` | Auth (свои билеты на это событие) |
| DELETE | `/api/v1/events/{slug}/tickets/{ticket_id}` | Auth (владелец) |
| GET | `/api/v1/tickets/my` | Auth |
| GET | `/api/v1/tickets/{ticket_id}/qr` | Auth (владелец) — возвращает PNG |

### Reviews — `/api/v1/events/{slug}/reviews`
| Метод | Путь | Доступ |
| --- | --- | :---: |
| POST | `/` | Attendee, купивший билет |
| GET | `/` | Public |
| DELETE | `/{review_id}` | Auth (владелец) / Moderator |

### Categories & Tags
| Метод | Путь | Доступ |
| --- | --- | :---: |
| GET / POST | `/api/v1/categories` | Public / Admin |
| GET / POST | `/api/v1/tags` | Public / Admin |

---

## 🔑 Ключи Redis

| Ключ | Значение | TTL | Назначение |
| --- | --- | :---: | --- |
| `blacklist:{jti}` | `"1"` | оставшееся время жизни токена | Отозванные access token (logout) |
| `verify:{token}` | `user_id` | 24ч | Верификация email |
| `reset:{token}` | `email` | 1ч | Сброс пароля |
| `login_attempts:{ip}` | count | 15 мин | Rate limit на попытки логина |
| `global_rate:{ip}` | count | 60с | Глобальный лимит 100 запросов/мин |
| `event:seats:{event_id}` | int | без TTL | Доступные места (защита от race condition) |
| `event:views:{event_id}` | int | без TTL | Счётчик просмотров, flush в БД каждые 5 мин |
| `popular_events` | JSON | 5 мин | Кэш топ-10 по просмотрам |

---

## ⏱ Задачи Celery

**Разовые (по событию):**
| Задача | Когда запускается | Поведение |
| --- | --- | --- |
| `send_verification_email` | после регистрации | ссылка верификации, retry при падении SMTP |
| `send_password_reset_email` | после forgot-password | ссылка сброса, retry при падении SMTP |
| `send_ticket_confirmation` | после успешной оплаты | детали события + QR-код вложением, retry ×3 / 60с |
| `send_event_cancellation` | событие → cancelled | письмо всем покупателям с paid-билетами, батчем |

**Периодические (Celery Beat):**
| Задача | Расписание | Поведение |
| --- | --- | --- |
| `send_event_reminders` | каждый час | напоминание покупателям событий, стартующих через ~24ч |
| `flush_view_counters` | каждые 5 мин | переносит `event:views:*` из Redis в поле `views` в БД, затем чистит ключи |
| `send_weekly_digest` | понедельник, 9:00 | топ-5 ближайших опубликованных событий всем активным пользователям |

---

## ⚠️ Формат ошибок

Любой ответ с ошибкой, независимо от статус-кода, имеет единую форму:

```json
{
  "error": "not_found",
  "message": "Мероприятие не найдено"
}
```

Ошибки валидации (`422`) дополнительно содержат массив `details`:

```json
{
  "error": "validation_error",
  "message": "Ошибка валидации входных данных",
  "details": [
    { "field": "starts_at", "message": "Дата начала должна быть в будущем" }
  ]
}
```

| Код `error` | HTTP статус | Когда |
| --- | :---: | --- |
| `unauthorized` | 401 | токен отсутствует, истёк или в blacklist |
| `forbidden` | 403 | недостаточно прав или не владелец ресурса |
| `not_found` | 404 | ресурс не найден |
| `conflict` | 409 | дублирование (email занят, мест нет) |
| `validation_error` | 422 | некорректные входные данные |
| `rate_limit_exceeded` | 429 | превышен лимит запросов |
| `internal_error` | 500 | необработанная ошибка сервера |

---

## 👥 Команда и распределение задач (кто что делает)

Команда из двух человек, бэклог разделён по эпикам. Полная детализация задач
(критерии приёмки, технические заметки, оценки времени) — в бэклоге проекта,
здесь — сводка.

### S1 — Foundation, Auth, User, Middleware, настройка Celery (~36–37.5ч)

| Эпик | Зона ответственности |
| --- | --- |
| **Project Foundation** | Настройка репозитория/веток, `Settings`, async DB engine + `get_db`, инициализация Alembic, Redis-клиент, generic `BaseRepository[T]`, а также API-контракт (Pydantic-схемы + роутеры-заглушки, возвращающие `501` для **всех** эндпоинтов из ТЗ, включая зону S2 — чтобы `/docs` и `/openapi.json` были полными с первого дня) |
| **Authentication** | Модель `User`, хеширование пароля + JWT-утилиты, регистрация, логин (с rate limiting), logout + blacklist токена, refresh, верификация email, сброс пароля, и общие DI-зависимости `get_current_user` / `require_role` / `require_verified`, от которых зависит всё остальное |
| **User Profile** | `GET/PATCH /users/me`, публичный профиль, загрузка аватара |
| **Middleware & Security** | CORS, логирование запросов, глобальные exception handlers (единый формат ошибок), глобальный rate-limit middleware |
| **Настройка Celery + базовые уведомления** | `core/celery.py` + скелет beat schedule, задача верификации email, задача сброса пароля |

> **S1 держит критический путь.** `get_current_user` и auth-зависимости должны
> быть готовы рано — эндпоинты Events/Tickets у S2 заблокированы без них.

### S2 — Categories, Events, Tickets, Reviews, Search, Notifications (~44–46ч)

| Эпик | Зона ответственности |
| --- | --- |
| **Categories & Tags** | Модели + association table, публичный GET / admin POST |
| **Events** | Модель `Event`, создание (генерация slug + get-or-create тегов), список с пагинацией, детали со счётчиком просмотров в Redis, обновление, машина состояний publish/cancel, кэш популярных событий, статистика продаж для организатора |
| **Ticketing System** | Модель `Ticket`, **защищённый от race condition флоу покупки** (самая сложная задача во всём бэклоге), отмена с ограничением в 2 часа, генерация/выдача QR-кода, список «мои билеты» |
| **Reviews** | Модель `Review` с уникальным constraint `(event_id, author_id)`, создание только для купивших билет, список + средний рейтинг, удаление |
| **Search & Discovery** | Расширяет список событий полнотекстовым поиском (`ILIKE`), фильтрами по категории/тегу/городу/дате/цене и всеми режимами сортировки |
| **Уведомления по событиям** | Email подтверждения билета (с QR-вложением), рассылка при отмене события, задачи-напоминания и дайджест по расписанию |

### Рекомендуемый порядок работы

1. **S1**: Foundation → модели/утилиты Auth → `get_current_user` (разблокирует S2)
2. **S2**: Categories/Tags → модель Event и CRUD (параллельно с работой S1 над auth, как только готовы заглушки API-контракта)
3. **S1**: остальные эндпоинты Auth, Middleware, настройка Celery
4. **S2**: флоу покупки билетов (нужны `get_current_user` и Celery от S1) → Reviews → Search
5. **Оба**: подключение уведомлений, затем совместное QA по демо-чеклисту клиента

---

## 🌿 Git Workflow

**Ветки**
```
main        — production-ready код, прямые пуши запрещены, только через PR
develop     — интеграционная ветка, всё сливается сюда
feature/*   — напр. feature/ticket-purchase
fix/*       — напр. fix/race-condition-seats
chore/*     — зависимости, конфиг, рефакторинг
```

**Коммиты** — [Conventional Commits](https://www.conventionalcommits.org/):
```
feat(auth): add JWT refresh token endpoint
fix(tickets): return seats to Redis on payment failure
chore(deps): add qrcode and aiosmtplib packages
```

**Pull Request**
1. Ветка от `develop`
2. PR с описанием что сделано и как проверить
3. Минимум один approve от второго участника команды перед merge
4. Автор мержит после approve, затем удаляет ветку

---

## ❓ Открытые вопросы / допущения

Следующие моменты не были закрыты с клиентом до начала разработки. Решения,
принятые командой самостоятельно, зафиксированы здесь — обновите таблицу,
когда появятся реальные ответы клиента.

| # | Вопрос | Принятое допущение |
| --- | --- | --- |
| 1 | Может ли организатор создать бесплатное мероприятие (`price = 0`)? | *заполнить* |
| 2 | Нужна ли модерация перед публикацией? | *заполнить* |
| 3 | Можно ли уменьшить вместимость после продажи части билетов? | *заполнить* |
| 4 | Нужны ли несколько типов билетов на событие (VIP/Стандарт)? | *заполнить* |
| 5 | Видит ли организатор контакты покупателей? | *заполнить* |
| 6 | Автоматический возврат денег при отмене или вручную? | *заполнить* |
| 7 | Есть ли возрастные ограничения (18+) на некоторые события? | *заполнить* |
| 8 | Нужен ли поиск по организатору? | *заполнить* |

---

## ✅ Критерии готовности (Definition of Done)

- [ ] Все эндпоинты задокументированы в Swagger (`/docs`)
- [ ] Покупка последнего билета двумя параллельными запросами обрабатывается корректно (без перепродажи)
- [ ] Email-уведомления отправляются асинхронно через Celery, никогда не inline в запросе
- [ ] Каждый ответ с ошибкой соответствует единому формату
- [ ] Код разделён по слоям router → service → repository во всех модулях
- [ ] `.env.example` присутствует, `.env` в `.gitignore`
- [ ] `alembic upgrade head` проходит без ошибок на пустой базе данных
- [ ] Все три роли (attendee, organizer, admin) вручную проверены через Swagger/Postman
- [ ] Открытые вопросы выше заполнены реальными решениями команды

---

<p align="center">
  <sub>Собрано командой из двух человек — от discovery-звонка с клиентом до защищённого от race condition флоу покупки билетов.</sub>
</p>