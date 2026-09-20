# База данных

СУБД - PostgreSQL 18. Доступ к данным выполняется только через SQL запросы (psycopg), ORM не используется. Схема, индексы, триггер и справочники создаются в [database/init.sql](../database/init.sql), тестовые данные - в [database/seed.sql](../database/seed.sql).

## Сущности и связи

В базе шесть таблиц. Три из них - главные связанные сущности (`depositors`, `deposits`, `contracts`), две - справочники (`countries`, `currencies`) и одна - пользователи (`users`).

Связи:

- `depositors.country_id -> countries.id` - у вкладчика одна страна.
- `deposits.depositor_id -> depositors.id` - вклад принадлежит одному вкладчику.
- `deposits.currency_id -> currencies.id` - у вклада одна валюта.
- `contracts.deposit_id -> deposits.id` - договор оборачивает ровно один вклад (ограничение `UNIQUE`, связь один к одному).
- `depositors.created_by`, `deposits.created_by`, `contracts.created_by -> users.id` - автор записи.

## Описание таблиц

### users

Обязательная сущность типа User с полями `username` и `password_hash`.

| Поле | Тип | Ограничения |
| --- | --- | --- |
| id | SERIAL | PRIMARY KEY |
| username | TEXT | UNIQUE, NOT NULL |
| email | TEXT | UNIQUE, NOT NULL |
| password_hash | TEXT | NOT NULL (bcrypt хеш) |
| status | TEXT | NOT NULL, DEFAULT 'Active' |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() |
| last_visit_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() |

### countries (справочник)

| Поле | Тип | Ограничения |
| --- | --- | --- |
| id | SERIAL | PRIMARY KEY |
| name | TEXT | UNIQUE, NOT NULL |

### currencies (справочник)

| Поле | Тип | Ограничения |
| --- | --- | --- |
| id | SERIAL | PRIMARY KEY |
| code | TEXT | UNIQUE, NOT NULL |

### depositors

| Поле | Тип | Ограничения |
| --- | --- | --- |
| id | SERIAL | PRIMARY KEY |
| first_name | TEXT | NOT NULL |
| last_name | TEXT | NOT NULL |
| date_of_birth | DATE | NOT NULL, проверка возраста триггером |
| country_id | INTEGER | NOT NULL, FK -> countries(id) |
| passport | TEXT | UNIQUE, NOT NULL |
| tin | TEXT | UNIQUE, NOT NULL (ИНН) |
| phone | TEXT | NOT NULL |
| email | TEXT | UNIQUE, NOT NULL |
| address | TEXT | NOT NULL |
| created_by | INTEGER | FK -> users(id) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() |

### deposits

| Поле | Тип | Ограничения |
| --- | --- | --- |
| id | SERIAL | PRIMARY KEY |
| depositor_id | INTEGER | NOT NULL, FK -> depositors(id) |
| currency_id | INTEGER | NOT NULL, FK -> currencies(id) |
| status | TEXT | NOT NULL (Active, Pending, Closed, Blocked) |
| amount | NUMERIC(15,2) | NOT NULL, CHECK (amount > 0) |
| interest_rate | NUMERIC(5,2) | NOT NULL, CHECK (0..100) |
| start_date | DATE | NOT NULL |
| end_date | DATE | NOT NULL, CHECK (end_date > start_date) |
| created_by | INTEGER | FK -> users(id) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() |

### contracts

| Поле | Тип | Ограничения |
| --- | --- | --- |
| id | SERIAL | PRIMARY KEY |
| deposit_id | INTEGER | NOT NULL, UNIQUE, FK -> deposits(id) |
| contract_date | DATE | NOT NULL |
| signing_status | TEXT | NOT NULL (Signed, Pending, Rejected) |
| description | TEXT | NOT NULL |
| special_conditions | TEXT | NOT NULL |
| created_by | INTEGER | FK -> users(id) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() |

## Нормализация

Схема приведена к третьей нормальной форме (3НФ).

Первая нормальная форма (1НФ). Все атрибуты атомарны, повторяющихся групп нет, у каждой таблицы есть первичный ключ. Например, у вкладчика имя и фамилия хранятся в отдельных полях.

Вторая нормальная форма (2НФ). Таблица в 1НФ, и каждый неключевой атрибут зависит от всего первичного ключа. Первичные ключи - одиночные суррогатные поля `id` (SERIAL), поэтому частичных зависимостей от части ключа быть не может. Данные, которые могли бы дублироваться (страна, валюта), вынесены в справочники и связаны по внешнему ключу.

Третья нормальная форма (3НФ). Таблица в 2НФ, и нет транзитивных зависимостей неключевых атрибутов друг от друга. Название страны хранится только в `countries`, код валюты - только в `currencies`, а в `depositors` и `deposits` лежат лишь идентификаторы `country_id` и `currency_id`. Расчётные величины (срок вклада, проценты, номера) не хранятся в базе, а вычисляются в сервисном слое или в запросах.

## Индексы

Индексы созданы под реальные сценарии сортировки и фильтрации.

```sql
-- depositors
CREATE INDEX depositors_created_at_index ON depositors (created_at DESC);
CREATE INDEX depositors_country_id_index ON depositors (country_id);

-- deposits
CREATE INDEX deposits_created_at_index ON deposits (created_at DESC);
CREATE INDEX deposits_depositor_id_index ON deposits (depositor_id);
CREATE INDEX deposits_status_index ON deposits (status);
CREATE INDEX deposits_start_date_index ON deposits (start_date);
CREATE INDEX deposits_end_date_index ON deposits (end_date);

-- contracts
CREATE INDEX contracts_created_at_index ON contracts (created_at DESC);
CREATE INDEX contracts_signing_status_index ON contracts (signing_status);
```

- Индексы по `created_at DESC` ускоряют сортировку списков по умолчанию.
- Индексы по внешним ключам (`country_id`, `depositor_id`) ускоряют соединения.
- Индексы по `status`, `signing_status`, `start_date`, `end_date` ускоряют фильтрацию и выборки для отчётов и плана возврата.

Уникальные ограничения (`username`, `email`, `passport`, `tin`, `deposit_id` в договорах) также создают уникальные индексы.

## Триггер и процедура

Возраст вкладчика проверяется на уровне базы: клиент должен быть не моложе 18 лет. Проверка реализована функцией на PL/pgSQL и триггером `BEFORE INSERT OR UPDATE`.

```sql
CREATE FUNCTION check_depositor_age() RETURNS trigger AS $$
BEGIN
    IF NEW.date_of_birth > CURRENT_DATE - INTERVAL '18 years' THEN
        RAISE EXCEPTION 'depositor must be at least 18 years old';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER depositors_min_age
    BEFORE INSERT OR UPDATE ON depositors
    FOR EACH ROW
    EXECUTE FUNCTION check_depositor_age();
```

Правило дублируется в сервисном слое (быстрый ответ пользователю), а триггер гарантирует его соблюдение на уровне данных.

## Бизнес-ограничения на уровне базы

- `amount > 0` - сумма вклада положительна.
- `interest_rate BETWEEN 0 AND 100` - ставка в допустимых границах.
- `end_date > start_date` - дата окончания позже даты начала.
- `contracts.deposit_id UNIQUE` - на один вклад не более одного договора.
- Уникальность `passport`, `tin`, `email` вкладчика.

## Поиск, фильтрация, сортировка и пагинация

Все операции выполняются на уровне SQL, а не в приложении.

- Поиск - условие `ILIKE` по нескольким колонкам (регистронезависимо).
- Фильтрация - по статусу вклада или статусу подписания договора.
- Сортировка - через белый список колонок (`ORDER BY` и направление), что защищает от инъекций в имени колонки.
- Пагинация - `LIMIT` и `OFFSET`, отдельным запросом считается общее число строк. Размеры страниц: 10, 25, 50.

Пример выборки вкладчиков с поиском и пагинацией:

```sql
SELECT d.id, d.first_name, d.last_name, d.date_of_birth, d.country_id, c.name,
       d.passport, d.tin, d.phone, d.email, d.address, d.created_at
FROM depositors d
JOIN countries c ON c.id = d.country_id
WHERE (d.first_name || ' ' || d.last_name) ILIKE %s
   OR d.email ILIKE %s
   OR c.name ILIKE %s
ORDER BY d.created_at DESC
LIMIT %s OFFSET %s;
```

Все значения передаются как параметры запроса (`%s`), а не подставляются в строку.

## Пример сложного запроса (отчёт по портфелю)

Отчёт по вкладчикам агрегирует суммы и доход по активным вкладам, приводит суммы к рублям через `CASE` по коду валюты и считает доход по формуле простых процентов:

```sql
SELECT dep.id, dep.first_name, dep.last_name,
       count(d.id),
       COALESCE(sum(d.amount * CASE c.code
              WHEN 'USD' THEN 87 WHEN 'EUR' THEN 100 WHEN 'RUB' THEN 1 ELSE 1 END), 0),
       COALESCE(sum(d.amount * CASE c.code
              WHEN 'USD' THEN 87 WHEN 'EUR' THEN 100 WHEN 'RUB' THEN 1 ELSE 1 END
              * d.interest_rate / 100 * (d.end_date - d.start_date) / 365), 0)
FROM depositors dep
JOIN deposits d   ON d.depositor_id = dep.id
JOIN currencies c ON c.id = d.currency_id
WHERE d.status = 'Active'
GROUP BY dep.id, dep.first_name, dep.last_name
ORDER BY 5 DESC
LIMIT %s OFFSET %s;
```

Денежные потоки (`/api/reports/cash-flow`) считаются в одном запросе через `sum(...) FILTER (WHERE ...)` за несколько периодов.

## Пересчёт валют

Суммы хранятся в исходной валюте вклада. Для сравнения и агрегации они приводятся к рублям по фиксированному курсу прямо в SQL: 1 USD = 87 RUB, 1 EUR = 100 RUB, 1 RUB = 1 RUB. Итог затем конвертируется в выбранную пользователем валюту в сервисном слое.

## Справочные и начальные данные

Справочники: 27 стран в `countries`, 3 валюты в `currencies` (USD, EUR, RUB).

Файл `seed.sql` добавляет пользователя `admin` (email `admin@depositone.com`, пароль как bcrypt хеш), 5 вкладчиков, 6 вкладов в разных валютах и статусах, 3 договора со статусами Signed, Pending, Rejected.

## Репликация Master-Slave

Реализована потоковая физическая репликация PostgreSQL.

Master ([database/master/replication.sh](../database/master/replication.sh)):

```bash
psql ... <<-EOSQL
    CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD '$REPLICATION_PASSWORD';
EOSQL
echo "host replication replicator all scram-sha-256" >> "$PGDATA/pg_hba.conf"
```

Контейнер `db` запускается с параметрами `wal_level=replica`, `max_wal_senders=10`, `max_replication_slots=10`.

Replica ([database/replica/entrypoint.sh](../database/replica/entrypoint.sh)):

```bash
if [ ! -s "$PGDATA/PG_VERSION" ]; then
    until pg_isready --host db ...; do sleep 2; done
    rm -rf "${PGDATA:?}"/*
    PGPASSWORD="$REPLICATION_PASSWORD" pg_basebackup --host db --username replicator \
        --pgdata "$PGDATA" --wal-method stream --write-recovery-conf --progress
fi
exec docker-entrypoint.sh postgres
```

Реплика при первом старте дожидается Master, снимает базовую копию и поднимается как standby в режиме только для чтения. Внешний порт реплики - 5433.

Проверка репликации после запуска:

```bash
# на Master: подключения репликации
docker compose exec db psql -U depositone -d depositone -c "SELECT client_addr, state FROM pg_stat_replication;"

# на реплике: должен вернуть true (режим восстановления, только чтение)
docker compose exec db_replica psql -U depositone -d depositone -c "SELECT pg_is_in_recovery();"
```
