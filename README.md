# 💰 Finly — Web-сервис для учёта личных финансов

**Finly** — это система учёта доходов и расходов с REST API, Telegram-ботом и аналитикой.  
Разработан как выпускная квалификационная работа в КФУ (2025).

---

## 🚀 Стек и зависимости

### 📦 Backend:
- `Python 3.11`
- `Flask` + `Flask-RESTX` (документирование)
- `Flask-JWT-Extended` (авторизация)
- `Flask-SQLAlchemy` + `Marshmallow` (ORM + сериализация)
- `aiohttp` (для async-запросов к внешним API)
- `Flask-Swagger-UI` (Swagger для документации)

### 🗄️ База данных:
- PostgreSQL
- `psycopg2-binary`
- SQLAlchemy

### 🤖 Telegram Bot:
- `Aiogram`

### 🧪 Тестирование:
- `pytest`, `pytest-flask`, `pytest-cov`, `coverage`

### ☁️ Интеграции:
- `ЦБ РФ API` (курсы валют)
- `Binance API` (курсы крипто-валют)
- `Yandex Cloud` (облачная реализация БД)
- `Yandex DataLens` (визуализация аналитики)

---

## 🧩 Основной функционал

- 📥 Ведение доходов и расходов
- 🗃️ Категоризация и фильтрация транзакций
- 📊 Финансовая аналитика (веб + Telegram)
- 💸 Поддержка мультивалютности
- 🔐 JWT-авторизация
- 🤖 Telegram-бот с быстрым вводом операций и просмотром отчётов

---

## 🖥️ Интерфейс

### Telegram:
<div align="center">
  <img src="https://raw.githubusercontent.com/iseq1/finly/main/documents/TG-interface.gif" width="75%" />
</div>

### Web:

<div align="center">
  <img src="https://raw.githubusercontent.com/iseq1/finly/main/documents/WEB-interface.gif" width="75%" />
</div>

---

## 📦 Установка и запуск

### 💻 Локально:

```bash
git clone https://github.com/iseq1/finly.git
```
Создайте `.env` файл по примеру `.env.example` в директории `backend/web-service`


#### API-сервер:
```bash
cd finly/backend/web-service
python -m venv venv
source venv/bin/activate  # или .\venv\Scripts\activate на Windows
pip install -r requirements.txt
python init_db.py
python seed_db.py
python run_dev.py
```

#### TG-bot:
```bash
cd finly/backend/telegram
python -m venv venv
source venv/bin/activate  # или .\venv\Scripts\activate на Windows
pip install -r requirements.txt
python tg_run.py
```

#### Web-interface:
```bash
cd finly/frontend
python -m http.server 7018
```
## API Документация

#### После запуска приложения документация Swagger будет доступна по адресу: `http://localhost:5000/api/docs`
---

## 📬 Контакты

- Telegram: [@atlantiee](https://t.me/atlantiee)
- Email: egorka.mironov.2003@mail.ru
- GitHub: [iseq1](https://github.com/iseq1)
