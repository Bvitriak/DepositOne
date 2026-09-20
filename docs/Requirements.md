# Требования и их выполнение

Документ сопоставляет требования задания с их реализацией в DepositOne и указывает, где именно каждое требование выполнено.

## Инструменты

| Требование | Реализация |
| --- | --- |
| Backend: Python, Flask, FastAPI | Core на FastAPI, Supporting на Flask |
| Frontend: HTML, CSS, JavaScript | Статические страницы в [frontend/](../frontend) |
| База данных: PostgreSQL 18 | Образ `postgres:18` в [docker-compose.yml](../docker-compose.yml) |

## Функциональные требования

### Web приложение реализует идею из аннотации

Учёт вкладчиков, вкладов и договоров, аналитика, отчёты и план возврата. Идея описана в [ANNOTATION.md](ANNOTATION.md), сценарии - в [UserGuide.md](UserGuide.md).

### Регистрация и вход пользователей + JWT

- Регистрация и вход: [auth_service.py](../backend/supporting/services/auth_service.py), маршруты [auth_routes.py](../backend/supporting/routes/auth_routes.py).
- Выпуск и проверка JWT (HS256, срок 1 час): [supporting/utils/auth.py](../backend/supporting/utils/auth.py), [core/utils/auth.py](../backend/core/utils/auth.py).
- Пароли хранятся в виде bcrypt хеша, открытый пароль не сохраняется.

### Не менее трёх связанных сущностей, нормализация минимум до 3НФ

Главные связанные сущности: `depositors`, `deposits`, `contracts` (плюс справочники `countries`, `currencies` и `users`). Схема приведена к 3НФ. Обоснование - в [Database.md](Database.md).

### Резервные ответы при недоступности сервисов

- База недоступна: `503 {"error": "database unavailable", "fallback": true}` ([core/utils/db.py](../backend/core/utils/db.py), [supporting/utils/db.py](../backend/supporting/utils/db.py)).
- Необработанная ошибка: `500 {"error": "internal server error", "fallback": true}` (обработчики в [main.py](../backend/core/main.py) и [app.py](../backend/supporting/app.py)).
- Фронтенд показывает резервные состояния (`Service Unavailable`, `N/A`, встроенный текст About).

### Два сервиса разными фреймворками

1. Core / Business (FastAPI) - бизнес-логика и главные сущности.
2. Supporting (Flask) - API Gateway для отчётности, аналитики, авторизации и уведомлений в формате JSON.

Разделение описано в [Architecture.md](Architecture.md).

### Поиск, фильтрация, сортировка и пагинация на уровне запросов к БД

Реализовано в репозиториях через `ILIKE`, `WHERE`, белый список `ORDER BY`, `LIMIT`/`OFFSET` и отдельный запрос подсчёта. Примеры - в [Database.md](Database.md).

### Модуль для CRUD операций

Полный CRUD для вкладчиков, вкладов и договоров (сервисы и репозитории Core), эндпоинты - в [Api.md](Api.md).

### Сущность User с полями user_name и password_hash

Таблица `users` содержит `username` и `password_hash` (см. [Database.md](Database.md)).

### Защита маршрутов от неавторизованных пользователей

- Supporting - декоратор `token_required`.
- Core - зависимость `require_user`.
- Незащищённые: регистрация, вход, сброс пароля, `/api/about`, `/api/hash/{str}`.

### Запрет ORM, только SQL

Доступ к данным - только через psycopg с параметризованными SQL запросами. ORM в проекте нет (см. репозитории в `backend/*/repositories`).

### Репликация Master-Slave

Потоковая физическая репликация PostgreSQL: контейнеры `db` (Master) и `db_replica` (Slave). Скрипты - [master/replication.sh](../database/master/replication.sh) и [replica/entrypoint.sh](../database/replica/entrypoint.sh). Подробно в [Database.md](Database.md).

### Эндпоинт /dashboard с диаграммами на Highcharts

Страница `/dashboard` защищена, диаграммы строятся на Highcharts ([dashboard.js](../frontend/js/dashboard/dashboard.js), [dashboard.html](../frontend/pages/dashboard/dashboard.html)).

### Эндпоинт /<username> с информацией и кнопкой обновления токена, защищён

Маршрут `/<username>` (nginx) отдаёт страницу профиля. Данные - из защищённого `GET /api/profile`, обновление токена - `POST /api/profile/token` по кнопке "Release Token" ([profile.js](../frontend/js/profile/profile.js)).

### Эндпоинт /about (HTML) и /api/about (JSON) из about.json

`/about` - HTML страница с кастомным дизайном ([about.html](../frontend/pages/about/about.html)). `/api/about` - JSON из [about.json](../backend/supporting/about.json) ([about_service.py](../backend/supporting/services/about_service.py)).

### Эндпоинт /api/hash/{str}

Возвращает `{"request": ..., "result": ...}` c SHA-256 хешем ([hash_service.py](../backend/supporting/services/hash_service.py)).

## Задачи FullStack

| Задача | Где выполнено |
| --- | --- |
| Пользовательские интерфейсы (HTML, CSS, JS) | [frontend/](../frontend) |
| Работа с фреймворками | FastAPI (Core), Flask (Supporting) |
| Взаимодействие интерфейса с сервером | [js/shared/request.js](../frontend/js/shared/request.js), Nginx |
| Серверная логика и API | Слои Controllers, Services, Routes |
| Работа с базами данных | Слой Repositories, [init.sql](../database/init.sql) |
| Выбор технологического стека | [ANNOTATION.md](ANNOTATION.md) |
| Проектирование взаимодействия фронт/бэк | [Architecture.md](Architecture.md) |
| Контроль качества кода во всех слоях | Единый слоистый шаблон, простой код |

## Задачи Database Engineer

| Задача | Где выполнено |
| --- | --- |
| Проектирование схемы (нормализация, связи) | [Database.md](Database.md), [init.sql](../database/init.sql) |
| Сложные запросы, процедуры и триггеры | Функция и триггер проверки возраста, агрегаты отчётов |
| Оптимизация запросов и индексация | Индексы под сортировку и фильтры |
| Настройка репликации | Master-Slave, скрипты в [database/](../database) |

## Организация репозитория и Git

| Требование | Реализация |
| --- | --- |
| Ветка `main` с README | Присутствует, README на русском |
| Ветка `dev` для интеграции | Присутствует |
| Ветки `feature/<username>/<task-name>` | Например `feature/bvitriak/backend` |
| Ветки `release/vX.Y` | Формат зафиксирован в [CONTRIBUTING](../.github/CONTRIBUTING.md) |
| Один коммит = одно логическое изменение | Соблюдается |
| Формат `<type>: <short description>`, en | Соблюдается (feat, fix, docs, refactor и т.д.) |
