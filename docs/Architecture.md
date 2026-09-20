# Архитектура

Документ описывает устройство DepositOne: сервисы, слои бэкенда, взаимодействие фронтенда и бэкенда, шлюз, инфраструктуру, репликацию базы данных и механизм резервных ответов.

## Общая схема

Браузер обращается к Nginx (порт 8080). Nginx отдаёт статику фронтенда и проксирует запросы `/api/*` в нужный сервис. Сервис Core (FastAPI, порт 8002) и сервис Supporting (Flask, порт 8001) читают и пишут данные в базу PostgreSQL. Основная база (Master, порт 5432) реплицируется на реплику только для чтения (Slave, порт 5433).

Приложение состоит из пяти контейнеров, описанных в [docker-compose.yml](../docker-compose.yml):

- `frontend` - Nginx, отдаёт статику и проксирует запросы к API.
- `core` - основной бизнес-сервис на FastAPI.
- `supporting` - вспомогательный сервис на Flask.
- `db` - основная база данных PostgreSQL (Master).
- `db_replica` - реплика только для чтения (Slave).

## Два сервиса на разных фреймворках

Требование задания - реализовать два сервиса разными фреймворками. В DepositOne роли разделены так.

### Core / Business (FastAPI, порт 8002)

Основная бизнес-логика и работа с главными сущностями. Отвечает за:

- CRUD вкладчиков, вкладов и договоров;
- справочники стран и валют;
- расчёт срока, начисленных и итоговых процентов;
- сводку по портфелю (`/api/portfolio`);
- план возврата и приоритеты выплат (`/api/plans`).

Точка входа - [backend/core/main.py](../backend/core/main.py). Роутеры подключаются к приложению FastAPI, для защищённых маршрутов используется зависимость `require_user`.

### Supporting (Flask, порт 8001)

Вспомогательный сервис в роли API Gateway для отчётности, аналитики, авторизации и уведомлений. Возвращает данные в формате JSON. Отвечает за:

- регистрацию, вход и сброс пароля (`/api/register`, `/api/login`, `/api/reset-password/*`);
- профиль пользователя и обновление токена (`/api/profile`, `/api/profile/token`);
- каркас аналитической панели (`/api/dashboard`);
- отчёты и денежные потоки (`/api/reports`, `/api/reports/cash-flow`);
- уведомления (`/api/notifications`);
- описание проекта (`/api/about`), список API (`/api/apis`), хеш строки (`/api/hash/{str}`).

Точка входа - [backend/supporting/app.py](../backend/supporting/app.py). Маршруты регистрируются как Blueprint, защита выполняется декоратором `token_required`.

## Слоистая структура бэкенда

Оба сервиса построены по одному шаблону из пяти слоёв. Запрос проходит по цепочке: Routes, Controllers, Services, Repositories, Models. Каждый слой имеет одну зону ответственности.

| Слой | Ответственность |
| --- | --- |
| Routes | URL, HTTP методы, подключение защиты и соединения с БД |
| Controllers | Чтение тела и параметров, проверка обязательных полей, коды ответа |
| Services | Бизнес-правила, валидация значений, расчёты, сериализация ответа |
| Repositories | SQL запросы к PostgreSQL через psycopg, без ORM |
| Models | Датаклассы, описывающие строку таблицы или агрегат |

Пример вертикали для вкладчиков в сервисе Core:

- [routes/depositor_routes.py](../backend/core/routes/depositor_routes.py)
- [controllers/depositor_controller.py](../backend/core/controllers/depositor_controller.py)
- [services/depositor_service.py](../backend/core/services/depositor_service.py)
- [repositories/depositor_repository.py](../backend/core/repositories/depositor_repository.py)
- [models/depositor.py](../backend/core/models/depositor.py)

## Путь запроса

На примере создания вклада `POST /api/deposits`:

1. Браузер отправляет запрос с заголовком `Authorization: Bearer <token>`.
2. Nginx по префиксу `/api/deposits` проксирует запрос в сервис Core.
3. Роут проверяет токен зависимостью `require_user` и открывает соединение с БД зависимостью `get_connection`.
4. Контроллер собирает payload из тела, проверяет обязательные поля.
5. Сервис валидирует значения (существование вкладчика и валюты, границы суммы и ставки, корректность дат) и вызывает репозиторий.
6. Репозиторий выполняет `INSERT` и возвращает созданную запись.
7. Сервис сериализует запись, добавляет расчёты и возвращает её контроллеру.
8. Контроллер отдаёт JSON и код `201`.

## Шлюз и маршрутизация (Nginx)

Файл [nginx.conf](../nginx.conf) отдаёт статические файлы фронтенда и проксирует запросы `/api/*` в нужный сервис.

- В сервис Core: `/api/depositors`, `/api/countries`, `/api/deposits`, `/api/currencies`, `/api/contracts`, `/api/plans`, `/api/portfolio`.
- В сервис Supporting: остальные `/api/`.

Маршруты страниц:

- `/about` отдаёт страницу описания проекта;
- `/dashboard` отдаёт аналитическую панель;
- `/<username>` (шаблон `^/[a-zA-Z0-9_]+$`) отдаёт страницу профиля;
- ошибки `404` и `5xx` перенаправляются на страницу ошибки с кодом в параметре.

## Взаимодействие фронтенда и бэкенда

Фронтенд - набор статических страниц без сборщика. Логика вынесена в общие модули в [frontend/js/shared](../frontend/js/shared):

- `request.js` - обёртки над `fetch`. Добавляет токен, обрабатывает `401` (переход на вход) и сетевые сбои.
- `list.js` - универсальный список: поиск, сортировка, фильтр, пагинация и резервный блок.
- `layout.js` - общая шапка, меню и подвал.
- `language.js` - переключение языка интерфейса (English / Русский).
- `currency.js`, `format.js` - валюта и форматирование.

Токен доступа хранится в `localStorage` и подставляется в каждый защищённый запрос.

## Аутентификация и защита маршрутов (JWT)

- При регистрации и входе Supporting выдаёт JWT (алгоритм `HS256`, срок жизни 1 час).
- Секрет берётся из переменной окружения `JWT_SECRET`, единой для обоих сервисов.
- Пароли хранятся в виде bcrypt хеша, открытый пароль в базе не сохраняется.
- Защищённые маршруты проверяют заголовок `Authorization: Bearer <token>`: Supporting - декоратор `token_required`, Core - зависимость `require_user`.
- Незащищённые маршруты: регистрация, вход, сброс пароля, `/api/about`, `/api/hash/{str}`.

Подробнее про эндпоинты и их защиту смотрите в [Api.md](Api.md).

## Резервные ответы

Приложение продолжает работать предсказуемо, даже если база или сервис недоступны.

Бэкенд:

- Если не удаётся подключиться к базе, оба сервиса возвращают `503 {"error": "database unavailable", "fallback": true}`.
- Необработанная ошибка возвращает `500 {"error": "internal server error", "fallback": true}`.

Фронтенд:

- Списки при сбое показывают блок "Service Unavailable" вместо данных.
- Панель, профиль и отчёты используют пустые значения `N/A`.
- Страница описания проекта показывает встроенный резервный текст, если `/api/about` не отвечает.
- Сетевые ошибки и коды `5xx` ведут на страницу ошибки с соответствующим кодом.

## Инфраструктура и запуск

- [Dockerfile](../Dockerfile) - многостадийная сборка: цели `frontend`, `supporting`, `core`.
- [docker-compose.yml](../docker-compose.yml) - оркестрация контейнеров, проверки здоровья, тома для данных.
- Переменные окружения задаются в файле `.env` (шаблон - [.env.example](../.env.example)).

Порты по умолчанию:

| Сервис | Внутренний порт | Внешний порт |
| --- | --- | --- |
| frontend (Nginx) | 80 | 8080 |
| core (FastAPI) | 8002 | 8002 |
| supporting (Flask) | 8001 | 8001 |
| db (Master) | 5432 | 5432 |
| db_replica (Slave) | 5432 | 5433 |

## Репликация базы данных (Master-Slave)

Основная база `db` работает в режиме Master, реплика `db_replica` - в режиме только для чтения (Slave). Механизм - потоковая физическая репликация PostgreSQL.

1. На Master при инициализации создаётся роль `replicator` с правом репликации, а в `pg_hba.conf` добавляется правило доступа ([database/master/replication.sh](../database/master/replication.sh)).
2. Master запускается с параметрами `wal_level=replica`, `max_wal_senders=10`, `max_replication_slots=10`.
3. Реплика при первом старте ждёт готовности Master, делает базовую копию через `pg_basebackup --wal-method stream --write-recovery-conf` и поднимается как standby ([database/replica/entrypoint.sh](../database/replica/entrypoint.sh)).

Подробности схемы, индексов, триггеров и запросов - в [Database.md](Database.md).

## Структура репозитория

- `backend/core` - сервис Core (FastAPI): controllers, models, repositories, routes, services, utils, config.py, database.py, main.py.
- `backend/supporting` - сервис Supporting (Flask): те же слои плюс about.json и app.py.
- `database` - init.sql, seed.sql, master/replication.sh, replica/entrypoint.sh.
- `frontend` - assets, css, js, pages, index.html.
- `docs` - документация проекта.
- `.github` - CI, шаблоны, политики.
- `docker-compose.yml`, `Dockerfile`, `nginx.conf` - инфраструктура.
