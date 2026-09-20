# Справочник API

Все ответы - в формате JSON. Защищённые эндпоинты требуют заголовок `Authorization: Bearer <token>`. Список эндпоинтов также доступен в приложении на странице API и через `GET /api/apis`.

## Базовые адреса

- Через шлюз Nginx: `http://localhost:8080/api/...` (рекомендуется).
- Напрямую в сервис Core: `http://localhost:8002/api/...`.
- Напрямую в сервис Supporting: `http://localhost:8001/api/...`.

## Коды ответов и резервные ответы

| Код | Значение |
| --- | --- |
| 200 | Успех |
| 201 | Ресурс создан |
| 400 | Ошибка валидации или неполные данные |
| 401 | Нет токена, токен неверен или истёк |
| 404 | Ресурс не найден |
| 409 | Конфликт (дубликат или запрет удаления) |
| 500 | Внутренняя ошибка, тело `{"error": ..., "fallback": true}` |
| 503 | База данных недоступна, тело `{"error": ..., "fallback": true}` |

## Сервис Supporting (Flask, порт 8001)

| Метод | Путь | Защита | Описание |
| --- | --- | --- | --- |
| POST | /api/register | нет | Регистрация пользователя, возвращает токен |
| POST | /api/login | нет | Вход, возвращает токен |
| POST | /api/reset-password/check | нет | Проверка аккаунта перед сбросом пароля |
| POST | /api/reset-password/confirm | нет | Сохранение нового пароля |
| GET | /api/about | нет | Данные о проекте из about.json |
| GET | /api/hash/{str} | нет | SHA-256 хеш строки |
| GET | /api/dashboard | JWT | Каркас данных аналитической панели |
| GET | /api/apis | JWT | Список доступных эндпоинтов |
| GET | /api/notifications | JWT | Ближайшие выплаты и договоры на подпись |
| GET | /api/profile | JWT | Карточка профиля текущего пользователя |
| POST | /api/profile/token | JWT | Выпуск нового токена доступа |
| GET | /api/reports | JWT | Отчёт по вкладчикам (поиск, сортировка, пагинация) |
| GET | /api/reports/cash-flow | JWT | Денежные потоки по периодам |

## Сервис Core (FastAPI, порт 8002)

Все эндпоинты защищены JWT.

### Вкладчики (Depositors)

| Метод | Путь | Описание |
| --- | --- | --- |
| GET | /api/depositors | Список с поиском, сортировкой, пагинацией |
| POST | /api/depositors | Создать карточку вкладчика |
| GET | /api/depositors/options | Список для выпадающих списков |
| GET | /api/depositors/{id} | Одна карточка вкладчика |
| PUT | /api/depositors/{id} | Обновить карточку |
| DELETE | /api/depositors/{id} | Удалить вкладчика без вкладов |

### Вклады (Deposits)

| Метод | Путь | Описание |
| --- | --- | --- |
| GET | /api/deposits | Список с поиском, фильтром, сортировкой, пагинацией |
| POST | /api/deposits | Открыть новый вклад |
| GET | /api/deposits/options | Вклады для форм договоров |
| GET | /api/deposits/stats | Счётчики и суммы по статусам и валютам |
| GET | /api/deposits/{id} | Один вклад с расчётом срока и процентов |
| PUT | /api/deposits/{id} | Обновить параметры вклада |
| DELETE | /api/deposits/{id} | Удалить вклад без договора |

### Договоры (Contracts)

| Метод | Путь | Описание |
| --- | --- | --- |
| GET | /api/contracts | Список с поиском, фильтром, сортировкой, пагинацией |
| POST | /api/contracts | Создать договор для вклада |
| GET | /api/contracts/{id} | Один договор с данными вклада |
| PUT | /api/contracts/{id} | Обновить условия договора |
| DELETE | /api/contracts/{id} | Удалить договор |

### План возврата (Plans)

| Метод | Путь | Описание |
| --- | --- | --- |
| GET | /api/plans | Список планов возврата (поиск, пагинация) |
| GET | /api/plans/summary | Итоги месяца и приоритетные выплаты |
| GET | /api/plans/{deposit_id} | План возврата одного вклада с графиком |

### Прочее (Core)

| Метод | Путь | Описание |
| --- | --- | --- |
| GET | /api/portfolio | Итоги портфеля и операций по договорам |
| GET | /api/countries | Справочник стран для форм вкладчиков |
| GET | /api/currencies | Справочник валют для форм вкладов |

## Общие параметры списков

Эндпоинты со списками принимают параметры строки запроса.

| Параметр | Значение |
| --- | --- |
| search | Строка поиска (регистронезависимо) |
| sort | Ключ сортировки (свой набор у каждого списка) |
| order | `asc` или `desc` |
| page | Номер страницы (с 1) |
| page_size | Размер страницы: 10, 25 или 50 |
| status | Фильтр по статусу (вклады, договоры) |
| currency | Валюта вывода сумм: USD, EUR, RUB (отчёты, сводки) |

Ответ списка содержит массив элементов и поля `total`, `page`, `pages`, `page_size`.

## Обязательные эндпоинты задания

### Регистрация и вход

```
POST /api/register
{ "username": "operator", "email": "op@example.com", "password": "secret" }
-> 201 { "access_token": "<JWT>" }

POST /api/login
{ "email": "op@example.com", "password": "secret" }
-> 200 { "access_token": "<JWT>" }
```

### Профиль пользователя /<username> с обновлением токена

Страница `/<username>` защищена: без токена происходит переход на вход. Данные берутся из защищённого `GET /api/profile`, кнопка "Release Token" вызывает `POST /api/profile/token` и выдаёт новый JWT.

```
GET /api/profile           (JWT)
-> 200 {
  "account_id": "U-0001",
  "nickname": "admin",
  "email": "admin@depositone.com",
  "status": "Active",
  "created": "18.09.2026",
  "last_visit": "20.09.2026"
}

POST /api/profile/token    (JWT)
-> 200 { "access_token": "<новый JWT>" }
```

### Описание проекта /about и /api/about

Маршрут `/about` возвращает HTML страницу с кастомным дизайном. Маршрут `/api/about` возвращает JSON, данные хранятся в файле [backend/supporting/about.json](../backend/supporting/about.json).

```
GET /api/about
-> 200 {
  "name": "DepositOne",
  "summary": "...",
  "description": "...",
  "author": "Bogdan Vitriak",
  "group": "OKBI-204B",
  "organization": "Moscow Technology Institute",
  "version": "1.0",
  "license": "MIT",
  "stack": [ ... ],
  "features": [ ... ]
}
```

### Хеш строки /api/hash/{str}

Принимает строку и возвращает её SHA-256 хеш.

```
GET /api/hash/hello
-> 200 {
  "request": "hello",
  "result": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
}
```

### Панель аналитика /dashboard

Страница `/dashboard` защищена и строит круговые диаграммы на Highcharts. Данные собираются из `GET /api/dashboard`, `GET /api/deposits/stats` и `GET /api/depositors`.
