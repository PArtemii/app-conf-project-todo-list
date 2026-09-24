"""Tool: get_tasks_by_priority.

Назначение:
    Возвращает задачи с указанным приоритетом.
    Использовать, когда пользователь спрашивает о задачах по приоритету.

Вход (input_data):
    priority: str  — обязателен, одно из 'high', 'medium', 'low'.
    status:   str  — необязателен, одно из 'todo', 'in_progress', 'done',
                     по умолчанию 'todo'.
    limit:    int  — необязателен, диапазон 1..50, по умолчанию 10.

Выход:
    JSON-строка.
    Успех: {"status": "ok", "count": 0, "items": []}
    Ошибка: {"status": "error", "message": "..."}
"""

import json
from typing import Any

VALID_PRIORITIES = ("high", "medium", "low")
VALID_STATUSES = ("todo", "in_progress", "done")
DEFAULT_STATUS = "todo"
DEFAULT_LIMIT = 10
MIN_LIMIT = 1
MAX_LIMIT = 50

# Мок-хранилище задач. В реальном проекте заменить на запрос к БД/API.
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
    """Формирует JSON-строку с ошибкой."""
    return json.dumps({"status": "error", "message": message}, ensure_ascii=False)


def _ok(items: list[dict[str, Any]]) -> str:
    """Формирует JSON-строку с успешным результатом."""
    return json.dumps(
        {"status": "ok", "count": len(items), "items": items},
        ensure_ascii=False,
    )


def _fetch_tasks() -> list[dict[str, Any]]:
    """Читает задачи из хранилища. Может бросить исключение."""
    return list(_TASKS)


def run(input_data: dict[str, Any]) -> str:
    """Основная точка входа Tool."""
    try:
        priority = input_data.get("priority")
        status = input_data.get("status", DEFAULT_STATUS)
        limit = input_data.get("limit", DEFAULT_LIMIT)

        # --- валидация priority ---
        if priority is None:
            return _fail("priority обязателен")
        if priority not in VALID_PRIORITIES:
            return _fail(
                f"priority должен быть 'high', 'medium' или 'low', получено '{priority}'"
            )

        # --- валидация status ---
        if status not in VALID_STATUSES:
            return _fail(
                f"status должен быть 'todo', 'in_progress' или 'done', получено '{status}'"
            )

        # --- валидация limit ---
        if not isinstance(limit, int) or isinstance(limit, bool):
            return _fail(f"limit должен быть целым числом, получено '{limit}'")
        if limit < MIN_LIMIT or limit > MAX_LIMIT:
            return _fail(
                f"limit должен быть в диапазоне {MIN_LIMIT}..{MAX_LIMIT}, получено {limit}"
            )

        # --- выборка ---
        try:
            tasks = _fetch_tasks()
        except Exception as exc:  # noqa: BLE001
            return _fail(f"ошибка хранилища: {exc}")

        filtered = [
            t for t in tasks
            if t.get("priority") == priority and t.get("status") == status
        ]
        return _ok(filtered[:limit])

    except Exception as exc:  # noqa: BLE001
        # Страховка: наружу не должно уходить никаких traceback.
        return _fail(f"внутренняя ошибка: {exc}")