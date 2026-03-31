# DepositOne

Информационная система учета депозитов физических лиц для небольшого банка или финансовой организации. 
Система автоматизирует работу с вкладчиками, депозитами, договорами, начислением процентов, кассовыми операциями и отчетностью.

## Функциональные возможности

- Управление данными вкладчиков.
- Открытие и ведение депозитов.
- Формирование и учет договоров по вкладам.
- Начисление процентов по депозитам.
- Учет кассовых операций по вкладам.
- Формирование приходно‑расходных отчетов.
- Сводные отчеты по вкладчикам.
- Планирование возвратов депозитов.

## Структура проекта

```text
deposit_bank/
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
├── LICENSE
├── database/
│   └── deposit_bank.db
├── app/
│   ├── __init__.py
│   ├── db.py
│   ├── routes.py
│   ├── models/
│   │   ├── depositor.py
│   │   ├── deposit.py
│   │   ├── contract.py
│   │   ├── transaction.py
│   │   └── interestAccrual.py
│   ├── services/
│   │   ├── contractService.py
│   │   ├── interestService.py
│   │   └── reportService.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── depositors.html
│   │   ├── createDepositor.html
│   │   ├── deposits.html
│   │   ├── createDeposit.html
│   │   ├── contracts.html
│   │   ├── createContract.html
│   │   ├── reports.html
│   │   └── returnPlan.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
```

### Описание основных файлов и каталогов

- `app.py` - создает приложение через и запускает сервер разработки.
- `requirements.txt` - список Python‑зависимостей.
- `.gitignore` - настройки для Git. 
- `README.md` - документация.  
- `LICENSE` - лицензия MIT.  
- `database/deposit_bank.db` - база данных.

#### База (`app/`)

- `app/__init__.py` - настройки приложения.
- `app/db.py` - инициализация базы данных.
- `app/routes.py` - HTTP‑маршруты и обработчики страниц.

#### Модели (`app/models/`)

- `depositor.py` - модель для хранения данных вкладчиков.
- `deposit.py` - модель для хранения данных вкладов.
- `contract.py` - модель для хранения договоров по вкладам.
- `transaction.py` - модель для учета кассовых операций.
- `interestAccrual.py` - модель для хранения начислений процентов.

#### Сервисы (`app/services/`)

- `contractService.py` - сервис для создания и подготовки данных договоров.
- `interestService.py` - сервис для расчета процентов и планов возвратов.
- `reportService.py` - сервис для формирования финансовых отчетов.

#### Шаблоны (`app/templates/`)

- `base.html` - базовый шаблон с навигацией.
- `index.html` - главная страница с ключевыми показателями.
- `depositors.html` - список вкладчиков.
- `createDepositor.html` - форма создания нового вкладчика.
- `deposits.html` - список вкладов.
- `createDeposit.html` - форма открытия вклада.
- `contracts.html` - список договоров. 
- `createContract.html` - форма создания договора по выбранному вкладу.
- `reports.html` - приходно‑расходные отчеты и сводка по вкладчикам.
- `returnPlan.html` - план возвратов вкладов на завтра и за месяц.

#### Статические файлы (`app/static/`)

- `css/style.css` - стили интерфейса.
- `js/main.js` - логика работы flash‑сообщений.

## Используемые технологии

- Python 3.x.
- Flask.
- Flask‑SQLAlchemy.
- SQLite. 
- HTML5, CSS3, JavaScript.

## Установка зависимостей и запуск

1. Установка зависимостей:

   ```bash
   pip install -r requirements.txt
   ```

2. Создать в корне проекта папку `database`

3. Запуск приложения:

   ```bash
   python3 app.py
   ```

4. Открыть в браузере `http://127.0.0.1:5000/`.

## Кто реализовал проект
- Богдан Витряк Олегович ОКБИ-204б - https://github.com/Bvitriak
