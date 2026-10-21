# To‑Do List API

Простой REST API для управления задачами с регистрацией и JWT‑аутентификацией.  
Проект создан для отработки инфраструктурных практик (Docker, CI/CD, тесты, наблюдаемость) на основе минимальной бизнес‑логики.

## Команда

- Пугач Артемий — Backend Developer
- Нестругина София — DevOps / Infrastructure
- Чубаркина Екатерина — CI/CD & Quality
- Панова Наталья — Deployment & Documentation

## Стек технологий

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy + Alembic
- Pydantic
- Docker, Docker Compose
- GitHub Actions
- pytest
- ruff, black, mypy

## API

Базовый URL: `http://localhost:8000`

| Метод | Путь       | Описание                                | Ответ |
|-------|------------|-----------------------------------------|-------|
| GET   | `/`        | Приветственное сообщение                | `{"message": "Hello World"}` |
| GET   | `/health`  | Проверка работоспособности сервиса      | `{"status": "healthy"}` |
| GET   | `/version` | Версия приложения и команда-владелец    | `{"version": "0.2.0", "team": "404"}` |

Интерактивная документация: `http://localhost:8000/docs` (Swagger UI) и `http://localhost:8000/redoc`.

### Примеры запросов

```bash
# macOS / Linux
curl http://localhost:8000/version

# Windows PowerShell
curl.exe http://localhost:8000/version
```

Ответ:

```json
{"version":"0.2.0","team":"404"}
```

Версия берётся из параметра `version` конструктора `FastAPI` в `main.py` и отображается в OpenAPI-схеме на `/docs`. Отдельной константы версии в проекте нет — это сделано намеренно, чтобы значение не разъезжалось.

## Статус

Проект в разработке.

## Установка и запуск

```bash
python -m venv venv
# Windows PowerShell
venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

## Лицензия

MIT

## Практика №4: конфигурация, безопасность и Docker

### Настройки окружения

Приложение использует `pydantic-settings` (`config.py`). Для локальной настройки скопируйте `.env.example` в `.env` и заполните параметры PostgreSQL. **Не добавляйте `.env` в Git.**

| Переменная | Назначение | Значение по умолчанию |
|---|---|---|
| `APP_ENV` | Режим `dev` или `prod` | `dev` |
| `DB_CONNECT_TIMEOUT` | Тайм-аут соединения с БД, 1–60 секунд | `3` |
| `DATABASE_URL` | URL подключения к PostgreSQL | Не задан |
| `POSTGRES_USER` | Пользователь PostgreSQL в Compose | Задаётся в `.env` |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL в Compose | Задаётся в `.env` |
| `POSTGRES_DB` | Имя базы данных в Compose | Задаётся в `.env` |

Docker Compose формирует `DATABASE_URL` из `POSTGRES_*` и передаёт его приложению. Для запуска вне Docker можно задать `DATABASE_URL` самостоятельно.

В режиме `dev` доступны `/docs`, `/redoc`, `/openapi.json`; в режиме `prod` эти адреса отключены.

### Запуск в Docker

```bash
docker compose up -d --build
docker compose ps
```

Проверка работоспособности: `http://localhost:8000/health`. Для остановки используйте `docker compose down` (без `-v`, если данные PostgreSQL нужно сохранить).

### Проверки перед коммитом

```bash
python -m pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Хуки проверяют пробелы, окончания файлов, YAML, TOML, размер добавляемых файлов, приватные ключи и потенциальные секреты (`detect-secrets`). Базовый файл проверки — `.secrets.baseline`. После автоматических исправлений проверьте `git status` и повторите запуск хуков.

### Оптимизация Docker

Dockerfile использует две стадии сборки, непривилегированного пользователя `appuser` (UID 10001) и `HEALTHCHECK`. Установка зависимостей кешируется отдельным слоем.

| Образ | Disk usage |
|---|---:|
| Исходный одноэтапный | 285 MB |
| Первый двухэтапный | 305 MB |
| Оптимизированный двухэтапный | 268 MB |

Итоговое уменьшение относительно исходного образа — **17 MB (около 6%)**.

Подробности решения — в [ADR 003](docs/adr/003-config-security-docker.md).
