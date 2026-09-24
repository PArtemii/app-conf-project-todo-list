"""Tool: create_task.

Назначение:
    Создаёт новую задачу. Использовать, когда пользователь просит
    добавить задачу в список.

Вход (input_data):
    title:    str — обязателен, непустой, длина 1..200.
    priority: str — необязателен, 'high' | 'medium' | 'low',
                    по умолчанию 'medium'.
    status:   str — необязателен, 'todo' | 'in_progress' | 'done',
                    по умолчанию 'todo'.

Выход:
    JSON-строка.
    Успех: {"status": "ok", "task": {"id": 8, "title": "...", ...}}
    Ошибка: {"status": "error", "message": "..."}
"""

import json
from typing import Any

VALID_PRIORITIES = ("high", "medium", "low")
VALID_STATUSES = ("todo", "in_progress", "done")
DEFAULT_PRIORITY = "medium"
DEFAULT_STATUS = "todo"
TITLE_MIN = 1
TITLE_MAX = 200

# Общее мок-хранилище с get_tasks_by_priority. В реальном проекте — БД/API.
_TASKS: list[dict[str, Any]] = [
    {"id": 1, "title": "Сделать отчёт", "priority": "high", "status": "todo"},
    {"id": 2, "title": "Позвонить клиенту", "priority": "high", "status": "in_progress"},
    {"id": 3, "title": "Обновить документацию", "priority": "medium", "status": "todo"},
    {"id": 4, "title": "Починить баг #42", "priority": "high", "status": "done"},
    {"id": 5, "title": "Разобрать бэклог", "priority": "low", "status": "todo"},
    {"id": 6, "title": "Ревью PR", "priority": "medium", "status": "in_progress"},
    {"id": 7, "title": "Написать тесты", "priority": "low", "status": "todo"},
]


def _fail(message: str) -> str:
    return json.dumps({"status": "error", "message": message}, ensure_ascii=False)


def _ok(task: dict[str, Any]) -> str:
    return json.dumps({"status": "ok", "task": task}, ensure_ascii=False)


def _next_id() -> int:
    return max((t["id"] for t in _TASKS), default=0) + 1


def _store(task: dict[str, Any]) -> None:
    """Сохраняет задачу. Может бросить исключение."""
    _TASKS.append(task)


def run(input_data: dict[str, Any]) -> str:
    """Основная точка входа Tool."""
    try:
        title = input_data.get("title")
        priority = input_data.get("priority", DEFAULT_PRIORITY)
        status = input_data.get("status", DEFAULT_STATUS)

        # --- валидация title ---
        if not isinstance(title, str) or not title.strip():
            return _fail("title обязателен и должен быть непустой строкой")
        if len(title) > TITLE_MAX:
            return _fail(f"title не должен превышать {TITLE_MAX} символов")

        # --- валидация priority ---
        if priority not in VALID_PRIORITIES:
            return _fail(
                f"priority должен быть 'high', 'medium' или 'low', получено '{priority}'"
            )

        # --- валидация status ---
        if status not in VALID_STATUSES:
            return _fail(
                f"status должен быть 'todo', 'in_progress' или 'done', получено '{status}'"
            )

        task = {
            "id": _next_id(),
            "title": title.strip(),
            "priority": priority,
            "status": status,
        }

        try:
            _store(task)
        except Exception as exc:  # noqa: BLE001
            return _fail(f"ошибка хранилища: {exc}")

        return _ok(task)

    except Exception as exc:  # noqa: BLE001
        return _fail(f"внутренняя ошибка: {exc}")