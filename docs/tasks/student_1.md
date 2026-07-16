# Студент 1 — 4-недельный план

**Зона ответственности:** Foundation · Auth · User · Middleware · Celery setup
**Итого:** ~36 часов
**Полный backlog:** [backlog.md](backlog.md) · **Timeline:** [timeline.md](timeline.md)

---

## Неделя 1 — Foundation (Jun 15–19) · ~9ч

> **Цель недели:** Запустить проект с нуля. К пятнице вечеру — `uvicorn` стартует,
> `alembic upgrade head` проходит, S2 может клонировать и работать.

| День | Задача | Оценка | Статус |
|---|---|---|---|
| Пн–Вт | `FOUND-001` Инициализация: GitHub, структура, зависимости | 2ч | [ ] |
| Пн–Вт | `FOUND-002` BaseSettings + .env + .env.example | 1ч | [ ] |
| Ср | `FOUND-003` Async SQLAlchemy: engine, session, Base, get_db | 2ч | [ ] |
| Ср | `FOUND-004` Alembic: init, env.py под async, первый `upgrade head` | 1.5ч | [ ] |
| Чт | `FOUND-005` Redis клиент + get_redis DI | 1ч | [ ] |
| Пт | `FOUND-006` Base Repository: get_by_id, create, update, delete | 2ч | [ ] |
| Пт | `FOUND-007` Pydantic схемы + заглушки: Auth + User эндпоинты | 1.5ч | [ ] |

**🔔 Sync 1 — Среда (17 июня):**
После `FOUND-003` — написать S2 что можно клонировать и начинать создавать модели.

**Чеклист конца недели:**
- [ ] `uvicorn app.main:app --reload` стартует без ошибок
- [ ] `alembic upgrade head` на пустой БД — ОК
- [ ] S2 склонировал репо, настроил `.env`, запустил проект
- [ ] `GET /docs` — Auth и User эндпоинты видны, все возвращают 501

---

## Неделя 2 — Auth (Jun 22–26) · ~10ч

> **Цель недели:** Полный Auth. `AUTH-009` — твой главный приоритет этой недели.
> Как только DI готовы — S2 может защищать эндпоинты. Не откладывай `AUTH-009` на конец.

| День | Задача | Оценка | Статус |
|---|---|---|---|
| Пн | `AUTH-001` User модель + enum ролей + миграция | 2ч | [ ] |
| Пн–Вт | `AUTH-002` Утилиты: hash_password, verify_password, create/decode JWT | 2ч | [ ] |
| Вт | `AUTH-003` POST /auth/register | 2.5ч | [ ] |
| Ср | `AUTH-004` POST /auth/login + rate limiting (Redis) | 2ч | [ ] |
| Чт | `AUTH-005` POST /auth/logout + blacklist в Redis | 1.5ч | [ ] |
| Чт | `AUTH-006` POST /auth/refresh (cookie → новый access token) | 1.5ч | [ ] |
| Пт | `AUTH-009` DI: get_current_user, require_role, require_verified | 2ч | [ ] |

> AUTH-007 (верификация email) и AUTH-008 (сброс пароля) перенесены на нед. 3
> — требуют Celery который ещё не настроен.

**🔔 Sync 2 — Пятница (28 июня):**
`AUTH-009` готова → написать S2: «DI доступны, начинай EVT-002 и защищай эндпоинты».

**Чеклист конца недели:**
- [ ] Полный flow в Swagger: register → login → получить access token
- [ ] Logout → повторный запрос с тем же токеном → 401
- [ ] `Depends(require_role(organizer))` для attendee → 403
- [ ] Rate limit: 6-я попытка логина → 429

---

## Неделя 3 — Auth finish + User + Middleware + Celery (Jun 29 – Jul 3) · ~12ч

> **Цель недели:** Закрыть все оставшиеся задачи. К пятнице — Celery worker
> работает и NOTIF-001 готова (S2 ждёт её для TKT-002).

| День | Задача | Оценка | Статус |
|---|---|---|---|
| Пн | `AUTH-007` POST /auth/verify-email (токен из Redis) | 2ч | [ ] |
| Пн | `AUTH-008` POST /auth/forgot-password + reset-password | 2ч | [ ] |
| Вт | `USR-001` GET/PATCH /users/me + GET /users/{username} | 2ч | [ ] |
| Ср | `USR-002` POST /users/me/avatar (UploadFile + StaticFiles) | 2ч | [ ] |
| Чт | `SEC-001` CORS + Logging middleware + Exception handlers | 2ч | [ ] |
| Чт | `SEC-002` Global Rate Limit middleware (100 req/min, Redis) | 1.5ч | [ ] |
| Пт | `NOTIF-001` Celery: setup + broker + beat schedule | 2ч | [ ] |
| Пт | `NOTIF-003` Celery tasks: send_verification_email + send_password_reset | 1.5ч | [ ] |

**🔔 Sync 3 — Пятница (3 июля):**
`NOTIF-001` готова → написать S2: «Celery запущен, можешь вызывать `.delay()`, начинай TKT-002».

**Чеклист конца недели:**
- [ ] Email верификации реально приходит на почту
- [ ] Avatar загружается, отдаётся через `/static/avatars/...`
- [ ] `celery -A app.core.celery worker --loglevel=info` — стартует без ошибок
- [ ] `celery -A app.core.celery beat --loglevel=info` — стартует без ошибок

---

## Неделя 4 — Интеграция и помощь (Jul 6–10) · ~5ч

> **Цель недели:** Помочь S2 закрыть сложные задачи, провести интеграционное
> тестирование всего проекта, подготовить Demo.

| День | Задача | Оценка | Статус |
|---|---|---|---|
| Пн–Вт | Помочь S2 с `TKT-002` если застрял (race condition — сложно) | — | [ ] |
| Ср | Интеграционный прогон: полный сценарий Demo через Swagger | 2ч | [ ] |
| Чт | Проверить формат ошибок во всех эндпоинтах (раздел 3.11 ТЗ) | 1ч | [ ] |
| Чт | Заполнить README по шаблону (раздел 6 ТЗ) | 1.5ч | [ ] |
| Пт | **🎯 Demo** | — | [ ] |

**Чеклист финала (раздел 7 ТЗ):**
- [ ] `alembic upgrade head` на чистой БД — все таблицы создаются
- [ ] Swagger `/docs` открывается, все эндпоинты задокументированы
- [ ] Race condition проверен: 2 параллельных запроса на последний билет
- [ ] Celery: email реально приходит на почту
- [ ] README заполнен по шаблону, допущения зафиксированы
- [ ] Все коммиты в Conventional Commits формате

---

## Важные детали по задачам

**AUTH-002 — jti в токене обязателен:**
`jti = str(uuid.uuid4())` добавить в payload. Нужен для blacklist при logout.
Без него нельзя реализовать AUTH-005.

**AUTH-004 — одинаковое сообщение на ошибку:**
«Неверный email или пароль» — одно сообщение для обоих случаев.
Разные сообщения позволяют перебрать базу email-ов (security).

**AUTH-005 — TTL blacklist = остаток жизни токена:**
`ttl = exp - int(datetime.now(UTC).timestamp())`.
Не фиксированные 15 минут — токен мог быть выдан 10 минут назад.

**AUTH-009 — сделать первым делом в нед. 2:**
S2 простаивает пока DI не готовы. Не откладывай на конец недели.
