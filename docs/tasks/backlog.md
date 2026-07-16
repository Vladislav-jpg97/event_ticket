# Event Ticketing Platform — Backlog

> Полный список задач проекта в формате реальной IT-компании.
> Инструмент аналог: Jira / Linear / GitHub Projects.

---

## Как читать этот документ

**Epic** — крупный блок функциональности (Auth, Events, Tickets...).
Каждый Epic разбит на **Tasks** — конкретные единицы работы.

**Формат задачи:**
- `Тип` — Feature (новая фича), Chore (настройка, инфраструктура), Fix (исправление)
- `Приоритет` — 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low
- `Оценка` — примерное время в часах (опытный джун)
- `Исполнитель` — S1 (Студент 1) или S2 (Студент 2)
- `Depends on` — задачи которые должны быть готовы раньше
- `Критерии приёмки` — конкретные вещи которые проверяют что задача сделана
- `Тех. заметки` — подсказки без готового кода

**Статусы:** `[ ]` To Do · `[~]` In Progress · `[x]` Done

---

## Распределение по студентам

| Студент | Эпики | Оценка |
|---|---|---|
| **S1** | Foundation, Auth, User, Middleware, Celery setup | ~37.5ч |
| **S2** | Categories, Events, Tickets, Reviews, Search, Notifications | ~46ч |

---

## EPIC 1 — Project Foundation

*Инфраструктура проекта. Всё остальное строится поверх этого эпика.*

---

### FOUND-001 — Инициализация проекта

**Тип:** Chore · **Приоритет:** 🔴 Critical · **Оценка:** 2ч · **Исполнитель:** S1
**Depends on:** —

**Описание:**
Создать репозиторий на GitHub, настроить структуру папок, установить зависимости,
подключить линтер. Это первая задача — без неё никто не может начать работу.

**Критерии приёмки:**
- [ ] Репозиторий создан на GitHub, ветки `main` и `develop` настроены
- [ ] Все зависимости из ТЗ (раздел 3.10) добавлены в `requirements.txt`
- [ ] Файл `.env.example` создан со всеми переменными из ТЗ (раздел 3.9)
- [ ] `.env` добавлен в `.gitignore`
- [ ] `uvicorn app.main:app --reload` запускается без ошибок (пустое приложение)

**Тех. заметки:**
- Команда `pip freeze > requirements.txt` после установки всех пакетов
- В `main.py` на старте достаточно `app = FastAPI(title=settings.app_name)`
- Структуру папок придумать самостоятельно (см. ТЗ раздел 3 — подсказок нет намеренно)

---

### FOUND-002 — Конфигурация (BaseSettings)

**Тип:** Chore · **Приоритет:** 🔴 Critical · **Оценка:** 1ч · **Исполнитель:** S1
**Depends on:** FOUND-001

**Описание:**
Создать класс `Settings` на базе `pydantic-settings`. Все переменные окружения
должны читаться только через него — никаких `os.environ` в коде.

**Критерии приёмки:**
- [ ] Класс `Settings` содержит все переменные из ТЗ раздел 3.9
- [ ] Создан глобальный объект `settings = Settings()` который импортируется везде
- [ ] При отсутствии обязательной переменной в `.env` приложение падает с понятной ошибкой при старте

**Тех. заметки:**
- `pydantic-settings` читает `.env` через `model_config = SettingsConfigDict(env_file=".env")`
- Типизировать все поля — `str`, `int`, `bool`. Pydantic сам приведёт типы из строк `.env`

---

### FOUND-003 — Настройка базы данных

**Тип:** Chore · **Приоритет:** 🔴 Critical · **Оценка:** 2ч · **Исполнитель:** S1
**Depends on:** FOUND-002

**Описание:**
Настроить async SQLAlchemy: engine, session factory, базовый класс моделей `Base`,
DI зависимость `get_db`. Без этого никто не сможет создать модели.

**Критерии приёмки:**
- [ ] `create_async_engine` принимает `DATABASE_URL` из settings
- [ ] `AsyncSessionLocal` создаётся через `async_sessionmaker`
- [ ] `get_db()` — async generator который yield-ит сессию и закрывает её в finally
- [ ] `Base` импортируется из одного места всеми моделями

**Тех. заметки:**
- `expire_on_commit=False` в `async_sessionmaker` — иначе объекты станут detached после commit
- Engine с `echo=settings.debug` — в debug режиме все SQL запросы будут в консоли

---

### FOUND-004 — Alembic инициализация

**Тип:** Chore · **Приоритет:** 🔴 Critical · **Оценка:** 1.5ч · **Исполнитель:** S1
**Depends on:** FOUND-003

**Описание:**
Настроить Alembic для работы с async SQLAlchemy. Базовая настройка `env.py`
чтобы `alembic revision --autogenerate` видел все модели.

**Критерии приёмки:**
- [ ] `alembic init alembic` выполнено, папка `alembic/` создана
- [ ] `alembic/env.py` настроен на async engine и импортирует `Base` из проекта
- [ ] `alembic upgrade head` на пустой БД проходит без ошибок
- [ ] `DATABASE_URL` в `alembic.ini` читается из `.env` (не хардкодить)

**Тех. заметки:**
- В `env.py` нужен `run_async_migrations()` через `asyncio.run()`
- Все модели должны быть импортированы в `env.py` (или в одном месте) иначе autogenerate их не увидит

---

### FOUND-005 — Redis клиент

**Тип:** Chore · **Приоритет:** 🟠 High · **Оценка:** 1ч · **Исполнитель:** S1
**Depends on:** FOUND-002

**Описание:**
Создать async Redis клиент и DI зависимость `get_redis`. Все части приложения
получают Redis через неё — нет глобальных подключений в бизнес-логике.

**Критерии приёмки:**
- [ ] `Redis.from_url(settings.redis_url, decode_responses=True)` создаётся при старте
- [ ] `get_redis()` доступна как FastAPI Depends
- [ ] `await redis.ping()` в startup event возвращает True

**Тех. заметки:**
- `decode_responses=True` — Redis возвращает строки а не байты
- Клиент создаётся один раз при старте, не в каждом запросе

---

### FOUND-006 — Base Repository

**Тип:** Chore · **Приоритет:** 🟠 High · **Оценка:** 2ч · **Исполнитель:** S1
**Depends on:** FOUND-003

**Описание:**
Создать generic базовый репозиторий с общими CRUD операциями.
Все конкретные репозитории наследуются от него и получают `get_by_id`,
`create`, `update`, `delete` бесплатно.

**Критерии приёмки:**
- [ ] `BaseRepository[T]` принимает модель и сессию через `__init__`
- [ ] Методы: `get_by_id`, `get_all`, `create`, `update`, `delete`
- [ ] `EventRepository(BaseRepository[Event])` может вызвать `get_by_id` без переопределения
- [ ] `update` принимает словарь и обновляет только переданные поля

**Тех. заметки:**
- Generic класс: `class BaseRepository[T]:` (Python 3.12+) или `BaseRepository(Generic[T])`
- `update` через `for key, value in data.items(): setattr(obj, key, value)`

---

### FOUND-007 — API Contract: Pydantic схемы + роутеры-заглушки

**Тип:** Chore · **Приоритет:** 🔴 Critical · **Оценка:** S1 — 1.5ч · S2 — 2ч · **Исполнитель:** S1 + S2
**Depends on:** FOUND-001

**Описание:**
Написать Pydantic схемы запросов/ответов и роутеры-заглушки для всех эндпоинтов
по ТЗ раздел 3. Реализация — `raise HTTPException(501)`. Цель — сгенерировать
полный `/openapi.json` до того как будет написана бизнес-логика.
Это позволяет фронтенду стартовать параллельно с бэкендом.

**Зона S1:** Auth + User (register, login, logout, refresh, verify-email, forgot-password, /users/me, /users/{username})
**Зона S2:** Categories, Tags, Events, Tickets, Reviews, Search

**Критерии приёмки:**
- [ ] `GET /docs` открывается — все эндпоинты из ТЗ раздел 3 видны
- [ ] Каждый эндпоинт имеет `response_model` с правильными полями из ТЗ раздел 3.12
- [ ] Запрос к любому эндпоинту возвращает `501 Not implemented` (не 404, не 422)
- [ ] `GET /openapi.json` возвращает валидный JSON со всеми схемами

**Тех. заметки:**
- Схемы брать строго из ТЗ раздел 3 — поля, типы, опциональность
- Роутеры подключить в `main.py` через `app.include_router()`
- `response_model` важнее тела функции — именно он попадает в OpenAPI
- Не смешивать схему запроса и ответа — `EventCreate` ≠ `EventResponse`

---

## EPIC 2 — Authentication & Authorization

*JWT авторизация, управление сессиями, верификация. Все защищённые эндпоинты зависят от этого эпика.*

---

### AUTH-001 — Модель User + миграция

**Тип:** Feature · **Приоритет:** 🔴 Critical · **Оценка:** 2ч · **Исполнитель:** S1
**Depends on:** FOUND-003, FOUND-004

**Описание:**
Создать SQLAlchemy модель `User` со всеми полями из ТЗ (раздел 3.1).
Сгенерировать миграцию.

**Критерии приёмки:**
- [ ] Все поля из ТЗ присутствуют с правильными типами и ограничениями
- [ ] `email` и `username` — уникальные индексы
- [ ] `role` — enum `attendee / organizer / admin`
- [ ] `TimestampMixin` подключён (created_at, updated_at)
- [ ] `alembic upgrade head` создаёт таблицу `users`

**Тех. заметки:**
- Enum для роли: `class UserRole(str, enum.Enum)` — `str` позволяет сравнивать со строками
- `Mapped[str]` с `mapped_column(unique=True, index=True)` для email и username

---

### AUTH-002 — Утилиты безопасности

**Тип:** Chore · **Приоритет:** 🔴 Critical · **Оценка:** 2ч · **Исполнитель:** S1
**Depends on:** FOUND-002

**Описание:**
Создать модуль `core/security.py` с функциями хеширования паролей и работы с JWT.
Это утилиты — они не знают про FastAPI, только чистая логика.

**Критерии приёмки:**
- [ ] `hash_password(plain: str) -> str` — возвращает bcrypt хеш
- [ ] `verify_password(plain: str, hashed: str) -> bool` — проверяет пароль
- [ ] `create_access_token(user_id: int) -> str` — JWT с `sub`, `jti` (UUID), `type: "access"`, `exp`
- [ ] `create_refresh_token(user_id: int) -> str` — JWT с `type: "refresh"`, TTL 30 дней
- [ ] `decode_token(token: str) -> dict` — декодирует и валидирует, бросает ValueError при невалидном

**Тех. заметки:**
- `jti` (JWT ID) = `str(uuid.uuid4())` — уникальный ID токена, нужен для blacklist при logout
- `passlib.context.CryptContext(schemes=["bcrypt"])`
- Время `exp` считать через `datetime.now(UTC) + timedelta(...)`

---

### AUTH-003 — Регистрация

**Тип:** Feature · **Приоритет:** 🔴 Critical · **Оценка:** 2.5ч · **Исполнитель:** S1
**Depends on:** AUTH-001, AUTH-002

**Описание:**
`POST /api/v1/auth/register` — создать пользователя, захешировать пароль,
запустить Celery задачу верификации email (задача NOTIF-001 должна быть готова).

**Критерии приёмки:**
- [ ] Валидация: email формат, username 3-30 символов, password минимум 8 символов
- [ ] При дублировании email → 409 с понятным сообщением
- [ ] При дублировании username → 409 с понятным сообщением
- [ ] Пароль в БД хранится только в хешированном виде
- [ ] Ответ 201 соответствует примеру из ТЗ раздел 3.12
- [ ] `is_verified: false` по умолчанию

**Тех. заметки:**
- Схема `UserCreate` отдельно от `UserResponse` — пароль не должен попасть в ответ никогда
- Celery задачу вызывать через `.delay()` — не ждать результата

---

### AUTH-004 — Логин

**Тип:** Feature · **Приоритет:** 🔴 Critical · **Оценка:** 2ч · **Исполнитель:** S1
**Depends on:** AUTH-002, AUTH-003

**Описание:**
`POST /api/v1/auth/login` — проверить credentials, вернуть access token в теле ответа
и refresh token в httponly cookie. С rate limiting на попытки.

**Критерии приёмки:**
- [ ] Rate limiting: после 5 неудачных попыток с одного IP → 429 на 15 минут
- [ ] При неверном email или пароле → 401 (одинаковое сообщение для обоих случаев — security)
- [ ] Access token в теле ответа `{"access_token": "...", "token_type": "bearer"}`
- [ ] Refresh token в `Set-Cookie: refresh_token=...; HttpOnly; SameSite=Lax`
- [ ] Счётчик попыток сбрасывается при успешном логине

**Тех. заметки:**
- Одинаковое сообщение на неверный email И неверный пароль — защита от enumeration атаки
- Cookie: `response.set_cookie("refresh_token", token, httponly=True, samesite="lax")`
- Rate limit счётчик: Redis `INCR login_attempts:{ip}` + `EXPIRE 900`

---

### AUTH-005 — Logout + Token Blacklist

**Тип:** Feature · **Приоритет:** 🟠 High · **Оценка:** 1.5ч · **Исполнитель:** S1
**Depends on:** AUTH-004, FOUND-005

**Описание:**
`POST /api/v1/auth/logout` — занести `jti` текущего access token в Redis blacklist
и удалить cookie с refresh token.

**Критерии приёмки:**
- [ ] `jti` из токена сохраняется в Redis с TTL = оставшееся время жизни токена
- [ ] Cookie с refresh token удаляется из браузера
- [ ] Повторный запрос с тем же access token → 401
- [ ] В `get_current_user` DI добавлена проверка blacklist

**Тех. заметки:**
- TTL для blacklist: `exp - int(datetime.now(UTC).timestamp())` — ровно до истечения токена
- `response.delete_cookie("refresh_token")` для удаления cookie
- Ключ в Redis: `blacklist:{jti}` = `"1"` (значение не важно, важен факт существования)

---

### AUTH-006 — Refresh Token

**Тип:** Feature · **Приоритет:** 🟠 High · **Оценка:** 1.5ч · **Исполнитель:** S1
**Depends on:** AUTH-004

**Описание:**
`POST /api/v1/auth/refresh` — принять refresh token из cookie,
выдать новый access token.

**Критерии приёмки:**
- [ ] Refresh token читается из cookie (не из тела запроса)
- [ ] Проверяется `type: "refresh"` в payload — access токен не принимается
- [ ] Refresh token проверяется на blacklist
- [ ] Возвращает новый access token
- [ ] При истёкшем или невалидном cookie → 401

**Тех. заметки:**
- `request.cookies.get("refresh_token")` для чтения cookie в FastAPI
- Создавать новый refresh token не нужно — только новый access token

---

### AUTH-007 — Верификация email

**Тип:** Feature · **Приоритет:** 🟠 High · **Оценка:** 2ч · **Исполнитель:** S1
**Depends on:** AUTH-003, NOTIF-002

**Описание:**
`POST /api/v1/auth/verify-email` — принять токен из письма,
проверить в Redis, обновить `is_verified = true`.

**Критерии приёмки:**
- [ ] Токен из Redis: `GET verify:{token}` возвращает `user_id`
- [ ] После верификации токен удаляется из Redis (нельзя использовать повторно)
- [ ] `user.is_verified = true` в БД
- [ ] Невалидный или истёкший токен → 400

**Тех. заметки:**
- TTL токена верификации при записи: 86400 секунд (24 часа)
- Удаление токена: `await redis.delete(f"verify:{token}")` сразу после успешного использования

---

### AUTH-008 — Сброс пароля

**Тип:** Feature · **Приоритет:** 🟡 Medium · **Оценка:** 2ч · **Исполнитель:** S1
**Depends on:** FOUND-005, NOTIF-003

**Описание:**
Два эндпоинта: `POST /auth/forgot-password` (создаёт токен в Redis и шлёт письмо)
и `POST /auth/reset-password` (принимает токен + новый пароль).

**Критерии приёмки:**
- [ ] `/forgot-password`: при несуществующем email — тот же успешный ответ (не раскрывать существование аккаунта)
- [ ] Токен сброса: UUID в Redis, ключ `reset:{token}`, значение `email`, TTL 3600 (1ч)
- [ ] `/reset-password`: токен проверяется, пароль хешируется и обновляется, токен удаляется
- [ ] После успешного сброса старые access tokens не инвалидируются (в рамках этого проекта)

**Тех. заметки:**
- Одинаковый ответ для существующего и несуществующего email — защита от enumeration

---

### AUTH-009 — DI зависимости

**Тип:** Chore · **Приоритет:** 🔴 Critical · **Оценка:** 2ч · **Исполнитель:** S1
**Depends on:** AUTH-005

**Описание:**
Создать переиспользуемые DI функции которые будут использоваться во всех
защищённых эндпоинтах. Без этого S2 не может начать работу с Events и Tickets.

**Критерии приёмки:**
- [ ] `get_current_user` — декодирует токен, проверяет blacklist, возвращает `User`
- [ ] `require_role(*roles)` — фабрика DI, бросает 403 если роль не подходит
- [ ] `require_verified` — бросает 403 если `is_verified=false`
- [ ] Тест: `Depends(require_role(UserRole.organizer))` блокирует attendee

**Тех. заметки:**
- `require_role` возвращает функцию (фабрика): `def require_role(*roles): async def checker(...): ...`
- `get_current_user` должен быть готов **первым** — S2 ждёт его для Events

---

## EPIC 3 — User Profile

---

### USR-001 — Профиль пользователя

**Тип:** Feature · **Приоритет:** 🟠 High · **Оценка:** 2ч · **Исполнитель:** S1
**Depends on:** AUTH-009

**Описание:**
`GET /api/v1/users/me` и `PATCH /api/v1/users/me` — просмотр и обновление профиля.

**Критерии приёмки:**
- [ ] GET возвращает профиль текущего пользователя (все поля кроме `hashed_password`)
- [ ] PATCH принимает только `bio` и опциональные поля — нельзя менять email/роль через этот эндпоинт
- [ ] Все поля в PATCH опциональны (схема `UserUpdate` с `Optional`)
- [ ] `GET /users/{username}` — публичный профиль (без email, без hashed_password)

**Тех. заметки:**
- `UserUpdate` схема: все поля `Optional[str] = None`, обновлять только не-None
- Публичный профиль: другая схема `UserPublicResponse` без приватных полей

---

### USR-002 — Загрузка аватара

**Тип:** Feature · **Приоритет:** 🟡 Medium · **Оценка:** 2ч · **Исполнитель:** S1
**Depends on:** USR-001

**Описание:**
`POST /api/v1/users/me/avatar` — загрузить изображение, сохранить на диск,
обновить `avatar_url` в БД.

**Критерии приёмки:**
- [ ] Принимает `multipart/form-data` с полем `file`
- [ ] Разрешённые типы: `image/jpeg`, `image/png`, `image/webp`
- [ ] Максимальный размер: 5 MB — при превышении 400
- [ ] Файл сохраняется в `static/avatars/` с уникальным именем
- [ ] `avatar_url` обновляется в БД
- [ ] `StaticFiles` подключён — файл доступен по HTTP

**Тех. заметки:**
- Уникальное имя файла: `f"{user.id}_{uuid4().hex[:8]}{suffix}"` — предотвращает коллизии
- Читать файл в память через `await file.read()`, проверить размер, затем записать

---

## EPIC 4 — Middleware & Security

---

### SEC-001 — CORS + Logging + Exception Handlers

**Тип:** Chore · **Приоритет:** 🟠 High · **Оценка:** 2ч · **Исполнитель:** S1
**Depends on:** FOUND-001

**Описание:**
Настроить три middleware: CORS для фронтенда, logging каждого запроса,
глобальные exception handlers для единого формата ошибок.

**Критерии приёмки:**
- [ ] CORS: `allow_credentials=True`, origins из settings
- [ ] Logging middleware: каждый запрос логируется — метод, путь, статус, время в мс
- [ ] `RequestValidationError` → `{"error": "validation_error", "message": ..., "details": [...]}`
- [ ] `HTTPException` → `{"error": "...", "message": "..."}`
- [ ] Порядок middleware: CORS → Rate Limit → Logging (CORS всегда первым)

**Тех. заметки:**
- Exception handler регистрируется через `@app.exception_handler(RequestValidationError)`
- Код ошибки (`error` field) — snake_case строка из таблицы ТЗ раздел 3.11

---

### SEC-002 — Global Rate Limit Middleware

**Тип:** Feature · **Приоритет:** 🟡 Medium · **Оценка:** 1.5ч · **Исполнитель:** S1
**Depends on:** FOUND-005, SEC-001

**Описание:**
Middleware класс который ограничивает 100 запросов в минуту с одного IP.
При превышении — 429 с сообщением.

**Критерии приёмки:**
- [ ] Счётчик в Redis: `INCR global_rate:{ip}` + `EXPIRE 60` при первом запросе
- [ ] При count > 100 → `JSONResponse(status=429, content={"error": "rate_limit_exceeded"})`
- [ ] Whitelist: `/docs`, `/redoc`, `/openapi.json` не ограничиваются
- [ ] Middleware наследуется от `BaseHTTPMiddleware`

---

## EPIC 5 — Categories & Tags

---

### CAT-001 — Модели Category + Tag + миграции

**Тип:** Feature · **Приоритет:** 🟠 High · **Оценка:** 1.5ч · **Исполнитель:** S2
**Depends on:** FOUND-003, FOUND-004

**Описание:**
Создать модели `Category`, `Tag` и association table `event_tags`. Миграции.

**Критерии приёмки:**
- [ ] `Category`: id, name (unique), slug (unique)
- [ ] `Tag`: id, name (unique)
- [ ] `event_tags` association table с FK на events и tags
- [ ] `alembic upgrade head` создаёт все три таблицы

**Тех. заметки:**
- Association table через `Table(...)` а не через отдельный класс модели
- Slug для категорий — задать вручную при создании (не автогенерировать)

---

### CAT-002 — CRUD категорий и тегов

**Тип:** Feature · **Приоритет:** 🟠 High · **Оценка:** 2ч · **Исполнитель:** S2
**Depends on:** CAT-001, AUTH-009

**Описание:**
Эндпоинты для работы с категориями (Admin) и тегами (Admin).
Публичные GET для всех.

**Критерии приёмки:**
- [ ] `GET /categories` — публичный список всех категорий
- [ ] `POST /categories` — только Admin, slug и name уникальны
- [ ] `GET /tags` — публичный список
- [ ] `POST /tags` — только Admin
- [ ] Дублирование name → 409

---

## EPIC 6 — Events

---

### EVT-001 — Модель Event + миграция

**Тип:** Feature · **Приоритет:** 🔴 Critical · **Оценка:** 2ч · **Исполнитель:** S2
**Depends on:** CAT-001, AUTH-001

**Описание:**
Создать модель `Event` со всеми полями из ТЗ (раздел 3.1). Relationships с
User, Category, Tag. Миграция.

**Критерии приёмки:**
- [ ] Все поля из ТЗ с правильными типами
- [ ] `status` — enum `draft/published/cancelled/completed`
- [ ] Relationship: `organizer → User`, `category → Category`, `tags → list[Tag]`
- [ ] `alembic upgrade head` создаёт `events` и `event_tags`
- [ ] `TimestampMixin` подключён

---

### EVT-002 — Создание события

**Тип:** Feature · **Приоритет:** 🔴 Critical · **Оценка:** 3ч · **Исполнитель:** S2
**Depends on:** EVT-001, AUTH-009, CAT-001

**Описание:**
`POST /api/v1/events` — создать событие в статусе `draft`.
Автоматически сгенерировать slug из title.

**Критерии приёмки:**
- [ ] Доступно только для `organizer` и `admin`
- [ ] Валидация по правилам из ТЗ раздел 3.7 (title, dates, capacity, price, tags)
- [ ] Slug генерируется автоматически: если `standup-v-malike` занят → `standup-v-malike-2`
- [ ] Теги принимаются как список строк, создаются если не существуют
- [ ] Статус при создании всегда `draft`
- [ ] Ответ соответствует `EventResponse` из ТЗ

**Тех. заметки:**
- Slug: `python-slugify` библиотека — `slugify(title)`
- Уникальность slug: цикл с суффиксом пока не найдётся свободный
- Теги: `get_or_create` — найти по name или создать новый

---

### EVT-003 — Список событий (базовый)

**Тип:** Feature · **Приоритет:** 🟠 High · **Оценка:** 2ч · **Исполнитель:** S2
**Depends on:** EVT-001

**Описание:**
`GET /api/v1/events` — базовый список опубликованных событий с пагинацией.
Фильтры и поиск добавляются в SRCH-001.

**Критерии приёмки:**
- [ ] Только `published` события для публичных пользователей
- [ ] Organizer видит свои `draft` события тоже
- [ ] Offset пагинация: `page`, `size` query params
- [ ] Ответ: `{items, total, page, pages}`
- [ ] Нет N+1 запросов — организатор и категория загружаются через `joinedload`

**Тех. заметки:**
- `selectinload` для тегов (many-to-many), `joinedload` для одиночных relations
- N+1: никогда не загружать relations внутри цикла — только через eager loading в запросе

---

### EVT-004 — Детали события + счётчик просмотров

**Тип:** Feature · **Приоритет:** 🟠 High · **Оценка:** 2ч · **Исполнитель:** S2
**Depends on:** EVT-003, FOUND-005

**Описание:**
`GET /api/v1/events/{slug}` — детали события.
При каждом запросе инкрементировать счётчик просмотров в Redis.

**Критерии приёмки:**
- [ ] `await redis.incr(f"event:views:{event.id}")` при каждом GET
- [ ] `views` в ответе берётся из Redis (не из БД) — актуальное значение
- [ ] `avg_rating` вычисляется из отзывов через SQL `func.avg`
- [ ] `available_seats` = `capacity` - `tickets_sold` (вычисляемое, не в БД)
- [ ] 404 если событие не найдено по slug

**Тех. заметки:**
- `views` из Redis: `int(await redis.get(f"event:views:{event.id}") or 0)`
- `available_seats` как Pydantic `computed_field` или вычислять в сервисе

---

### EVT-005 — Обновление события

**Тип:** Feature · **Приоритет:** 🟡 Medium · **Оценка:** 1.5ч · **Исполнитель:** S2
**Depends on:** EVT-002, AUTH-009

**Описание:**
`PATCH /api/v1/events/{slug}` — обновить поля события. Только в статусе `draft`.
Только автор или Admin.

**Критерии приёмки:**
- [ ] 403 если не автор и не admin
- [ ] 400 если статус не `draft`
- [ ] Обновляются только переданные поля (partial update)
- [ ] При изменении title — slug пересчитывается с проверкой уникальности

---

### EVT-006 — Смена статуса (FSM)

**Тип:** Feature · **Приоритет:** 🟠 High · **Оценка:** 2ч · **Исполнитель:** S2
**Depends on:** EVT-002, FOUND-005

**Описание:**
`PATCH /events/{slug}/publish` и `PATCH /events/{slug}/cancel`.
Логика машины состояний из ТЗ (раздел 2.3). При публикации — инициализировать счётчик мест в Redis.

**Критерии приёмки:**
- [ ] Недопустимый переход статуса → 400 с сообщением какой переход невозможен
- [ ] При публикации: `SET event:seats:{id} {capacity}` в Redis
- [ ] При отмене: Celery задача `send_event_cancellation.delay(event.id)`
- [ ] Только автор может публиковать. Автор или Admin может отменить.

**Тех. заметки:**
- FSM словарём: `TRANSITIONS = {draft: {published}, published: {cancelled, completed}, ...}`
- Проверка: `if new_status not in TRANSITIONS[current_status]: raise 400`

---

### EVT-007 — Популярные события (Redis кэш)

**Тип:** Feature · **Приоритет:** 🟡 Medium · **Оценка:** 2ч · **Исполнитель:** S2
**Depends on:** EVT-003, FOUND-005

**Описание:**
`GET /api/v1/events/popular` — топ-10 событий по просмотрам.
Кэшируется в Redis с TTL 5 минут.

**Критерии приёмки:**
- [ ] Первый запрос: идёт в БД, результат сохраняется в Redis как JSON
- [ ] Следующие запросы в течение 5 мин: отдаются из Redis без запроса в БД
- [ ] При публикации нового события — кэш инвалидируется (`DEL popular_events`)
- [ ] TTL ключа: 300 секунд

**Тех. заметки:**
- Сериализация: `json.dumps([item.model_dump() for item in events])`
- Десериализация обратно в Pydantic: `[EventShortResponse(**item) for item in json.loads(cached)]`

---

### EVT-008 — Статистика продаж для организатора

**Тип:** Feature · **Приоритет:** 🟢 Low · **Оценка:** 1.5ч · **Исполнитель:** S2
**Depends on:** EVT-002, TKT-001

**Описание:**
`GET /api/v1/events/{slug}/stats` — статистика продаж для организатора.

**Критерии приёмки:**
- [ ] Доступно только организатору-автору и Admin
- [ ] Возвращает: `total_tickets_sold`, `total_revenue`, `available_seats`, `occupancy_percent`
- [ ] `occupancy_percent` = `(tickets_sold / capacity) * 100` округлить до 1 знака

---

## EPIC 7 — Ticketing System

---

### TKT-001 — Модель Ticket + миграция

**Тип:** Feature · **Приоритет:** 🔴 Critical · **Оценка:** 1.5ч · **Исполнитель:** S2
**Depends on:** EVT-001, AUTH-001

**Описание:**
Создать модель `Ticket` со всеми полями из ТЗ. Миграция.

**Критерии приёмки:**
- [ ] Все поля из ТЗ (раздел 3.1)
- [ ] `uuid` генерируется автоматически через `default=lambda: str(uuid.uuid4())`
- [ ] `status` enum: `pending / paid / cancelled`
- [ ] Relationships с Event и User
- [ ] `alembic upgrade head` создаёт таблицу `tickets`

---

### TKT-002 — Покупка билетов (race condition)

**Тип:** Feature · **Приоритет:** 🔴 Critical · **Оценка:** 4ч · **Исполнитель:** S2
**Depends on:** TKT-001, EVT-006, FOUND-005

**Описание:**
`POST /api/v1/events/{slug}/tickets` — купить билеты.
Защита от race condition через атомарную операцию в Redis.
Это самая сложная задача проекта — см. ТЗ раздел 3.3.

**Критерии приёмки:**
- [ ] Только `attendee` может покупать
- [ ] `quantity` от 1 до 5
- [ ] Атомарная проверка и списание мест через Redis Lua script
- [ ] При нехватке мест → 409 с количеством доступных
- [ ] Ticket создаётся в БД со статусом `pending`
- [ ] Mock оплата → статус `paid`
- [ ] При падении "оплаты" → места возвращаются в Redis, ticket удаляется
- [ ] `total_price` фиксируется на момент покупки (не из текущей цены события)
- [ ] Celery задача на email запускается после успешной оплаты
- [ ] Ответ соответствует `TicketResponse` из ТЗ раздел 3.12

**Тех. заметки:**
- Lua script: атомарно проверяет счётчик и декрементирует — см. описание в ТЗ раздел 3.3
- `await redis.eval(script, 1, key, quantity)` — 1 ключ, quantity как аргумент
- Mock payment: функция которая всегда возвращает True (или можно рандомно для теста)

---

### TKT-003 — Отмена билета

**Тип:** Feature · **Приоритет:** 🟠 High · **Оценка:** 2ч · **Исполнитель:** S2
**Depends on:** TKT-002

**Описание:**
`DELETE /api/v1/tickets/{ticket_id}` — отменить билет.
Только за 2+ часа до начала события. Места возвращаются в Redis.

**Критерии приёмки:**
- [ ] Только владелец билета
- [ ] Если до начала события < 2 часа → 400 «Слишком поздно для отмены»
- [ ] Статус билета → `cancelled`
- [ ] `await redis.incrby(f"event:seats:{event_id}", ticket.quantity)` — вернуть места
- [ ] Отменить можно только `paid` билет (не `cancelled` повторно)

---

### TKT-004 — QR-код

**Тип:** Feature · **Приоритет:** 🟠 High · **Оценка:** 2ч · **Исполнитель:** S2
**Depends on:** TKT-002

**Описание:**
`GET /api/v1/tickets/{ticket_id}/qr` — вернуть QR-код как PNG изображение.
Содержимое QR: `ticket:{uuid}`. Доступ только владельцу.

**Критерии приёмки:**
- [ ] Возвращает `StreamingResponse` с `media_type="image/png"`
- [ ] QR содержит строку `ticket:{ticket.uuid}`
- [ ] 403 если запрашивает не владелец
- [ ] 404 если билет не найден
- [ ] В браузере (или Swagger) отображается QR-код

**Тех. заметки:**
- `qrcode.make(data)` → PIL Image → `io.BytesIO()` → `StreamingResponse`
- `img.save(buffer, format="PNG")` перед `buffer.seek(0)`

---

### TKT-005 — Мои билеты

**Тип:** Feature · **Приоритет:** 🟡 Medium · **Оценка:** 1ч · **Исполнитель:** S2
**Depends on:** TKT-001

**Описание:**
`GET /api/v1/tickets/my` — список всех билетов текущего пользователя.

**Критерии приёмки:**
- [ ] Только авторизованный пользователь
- [ ] Сортировка: сначала предстоящие события (по `starts_at`)
- [ ] Пагинация: `page` и `size`
- [ ] Каждый билет содержит вложенное краткое описание события

---

## EPIC 8 — Reviews

---

### RVW-001 — Модель Review + CRUD

**Тип:** Feature · **Приоритет:** 🟡 Medium · **Оценка:** 3ч · **Исполнитель:** S2
**Depends on:** EVT-001, TKT-001, AUTH-009

**Описание:**
Модель `Review`, миграция и все эндпоинты отзывов.
Отзыв можно оставить только если купил билет на это событие.

**Критерии приёмки:**
- [ ] Модель: id, event_id, author_id, rating (1-5), comment (nullable)
- [ ] Unique constraint на `(event_id, author_id)` — один отзыв на событие
- [ ] `POST /events/{slug}/reviews` — создать отзыв
- [ ] 403 если пользователь не купил билет на это событие (проверить по Ticket)
- [ ] 409 если уже оставил отзыв
- [ ] `GET /events/{slug}/reviews` — список с пагинацией + `avg_rating` в заголовке ответа
- [ ] `DELETE /reviews/{id}` — только автор или Admin

---

## EPIC 9 — Search & Discovery

---

### SRCH-001 — Поиск + фильтры + сортировка

**Тип:** Feature · **Приоритет:** 🟠 High · **Оценка:** 4ч · **Исполнитель:** S2
**Depends on:** EVT-003, CAT-001

**Описание:**
Расширить `GET /api/v1/events` всеми query params из ТЗ раздел 3.2.
Это продолжение EVT-003 — добавить фильтрацию, поиск и сортировку.

**Критерии приёмки:**
- [ ] `q` — ILIKE по `title`
- [ ] `category` — фильтр по `category.slug`
- [ ] `tag` — фильтр по `tag.name` через JOIN с `event_tags`
- [ ] `city` — точное совпадение (case-insensitive)
- [ ] `date_from` / `date_to` — фильтр по `starts_at`
- [ ] `price_min` / `price_max` — фильтр по `price`
- [ ] `sort` — все варианты из ТЗ (`date_asc`, `price_desc`, `rating`, `popular`)
- [ ] Фильтры можно комбинировать: `?city=Ташкент&category=standup&price_max=100000`

**Тех. заметки:**
- Строить запрос динамически: начать с `query = select(Event)`, добавлять `.where()` условия
- `sort=popular` — сортировка по `views` (из Redis: сначала flush в БД или отдельная логика)
- `sort=rating` — через subquery `avg(reviews.rating)` или вычислять на уровне запроса

---

## EPIC 10 — Celery & Notifications

---

### NOTIF-001 — Настройка Celery

**Тип:** Chore · **Приоритет:** 🟠 High · **Оценка:** 2ч · **Исполнитель:** S1
**Depends on:** FOUND-002, FOUND-005

**Описание:**
Создать `core/celery.py`, настроить broker (Redis), beat schedule для
периодических задач. Базовый тест что worker запускается.

**Критерии приёмки:**
- [ ] `celery -A app.core.celery worker --loglevel=info` запускается без ошибок
- [ ] `celery -A app.core.celery beat --loglevel=info` запускается без ошибок
- [ ] Broker: Redis (из `settings.redis_url`)
- [ ] Beat schedule содержит все 3 периодические задачи из ТЗ раздел 3.5

---

### NOTIF-002 — Email: подтверждение покупки

**Тип:** Feature · **Приоритет:** 🟠 High · **Оценка:** 2ч · **Исполнитель:** S2
**Depends on:** NOTIF-001, TKT-002

**Описание:**
Celery задача `send_ticket_confirmation` — отправить email после покупки
с деталями билета и QR-кодом в приложении.

**Критерии приёмки:**
- [ ] Задача вызывается в TKT-002 через `.delay(ticket_id)` после успешной оплаты
- [ ] Email содержит: название события, дату, место, количество билетов, цену
- [ ] QR-код прикреплён как вложение (PNG файл)
- [ ] При ошибке SMTP — повтор до 3 раз с задержкой 60 сек
- [ ] Письмо реально приходит на email (проверить на gmail или mailtrap)

**Тех. заметки:**
- `aiosmtplib` для async отправки. В Celery синхронный вариант через `smtplib` тоже допустим
- `bind=True, max_retries=3, default_retry_delay=60` в декораторе задачи

---

### NOTIF-003 — Email: верификация и сброс пароля

**Тип:** Feature · **Приоритет:** 🟠 High · **Оценка:** 1.5ч · **Исполнитель:** S1
**Depends on:** NOTIF-001

**Описание:**
Два Celery таска: `send_verification_email` (для AUTH-007) и `send_password_reset_email` (для AUTH-008).

**Критерии приёмки:**
- [ ] `send_verification_email(email, token)` — письмо со ссылкой верификации
- [ ] `send_password_reset_email(email, token)` — письмо со ссылкой сброса
- [ ] Ссылки содержат `settings.frontend_url` как базовый URL
- [ ] Оба таска с retry при ошибке SMTP

---

### NOTIF-004 — Email: отмена события

**Тип:** Feature · **Приоритет:** 🟠 High · **Оценка:** 1.5ч · **Исполнитель:** S2
**Depends on:** NOTIF-001, EVT-006

**Описание:**
Celery задача `send_event_cancellation` — уведомить всех покупателей
об отмене события организатором.

**Критерии приёмки:**
- [ ] Задача запускается в EVT-006 при переходе в `cancelled`
- [ ] Находит все `paid` билеты на событие, получает email покупателей
- [ ] Каждому отправляет письмо с названием события и датой
- [ ] Работает через batch (не N запросов к SMTP) — один запрос к БД, цикл отправки

---

### NOTIF-005 — Beat: напоминания + flush просмотров + дайджест

**Тип:** Feature · **Приоритет:** 🟡 Medium · **Оценка:** 3ч · **Исполнитель:** S2
**Depends on:** NOTIF-001, EVT-004

**Описание:**
Три периодические задачи для Celery Beat из ТЗ раздел 3.5.

**Критерии приёмки:**
- [ ] `send_event_reminders`: каждый час, находит события через 24ч, шлёт покупателям
- [ ] `flush_view_counters`: каждые 5 мин, переносит `event:views:*` из Redis в поле `views` в БД
- [ ] `send_weekly_digest`: понедельник 9:00, топ-5 ближайших событий всем активным пользователям
- [ ] `flush_view_counters` после переноса удаляет ключи из Redis (`GETDEL` или `GET` + `DEL`)

---

## Итоговое распределение

| Исполнитель | Задачи | Итого |
|---|---|---|
| **S1** | FOUND-001..006, AUTH-001..009, USR-001..002, SEC-001..002, NOTIF-001, NOTIF-003 | **~36ч** |
| **S2** | CAT-001..002, EVT-001..008, TKT-001..005, RVW-001, SRCH-001, NOTIF-002, NOTIF-004..005 | **~44ч** |
