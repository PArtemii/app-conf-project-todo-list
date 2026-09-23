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