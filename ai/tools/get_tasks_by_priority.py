"""Tool: get_tasks_by_priority.

Назначение:
    Возвращает задачи с указанным приоритетом и статусом.
    Использовать, когда пользователь спрашивает о задачах по приоритету.

Вход:
    priority: str  — обязателен, одно из 'high', 'medium', 'low'.
    status:   str  — необязателен, одно из 'todo', 'in_progress', 'done',
                     по умолчанию 'todo'.
    limit:    int  — необязателен, диапазон 1..50, по умолчанию 10.

Выход:
    JSON-строка.
    Успех: {"status": "ok", "count": N, "items": [...]}
    Ошибка: {"status": "error", "message": "..."}
"""

import json
from typing import Any

from crewai.tools import tool

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
    """Единый формат ошибки, который вернётся агенту."""
    return json.dumps({"status": "error", "message": message}, ensure_ascii=False)


@tool("get_tasks_by_priority")
def get_tasks_by_priority(priority: str, status: str = DEFAULT_STATUS, limit: int = DEFAULT_LIMIT) -> str:
    """Возвращает задачи с указанным приоритетом и статусом.

    Используй этот инструмент, когда пользователь спрашивает о своих задачах
    по приоритету — например, «покажи задачи с высоким приоритетом».

    Args:
        priority: приоритет задачи. Одно из: 'high', 'medium', 'low'. Обязателен.
        status: статус задачи. Одно из: 'todo', 'in_progress', 'done'.
                По умолчанию 'todo'.
        limit: максимальное число задач в ответе. Целое число от 1 до 50.
               По умолчанию 10.

    Returns:
        JSON-строка. При успехе: {"status": "ok", "count": N, "items": [...]}.
        При ошибке: {"status": "error", "message": "..."}.
    """
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

    # --- валидация limit ---
    if not isinstance(limit, int) or isinstance(limit, bool):
        return _fail(f"limit должен быть целым числом, получено '{limit}'")
    if limit < MIN_LIMIT or limit > MAX_LIMIT:
        return _fail(
            f"limit должен быть в диапазоне {MIN_LIMIT}..{MAX_LIMIT}, получено {limit}"
        )

    # --- выборка из хранилища ---
    try:
        tasks = list(_TASKS)
    except Exception as exc:  # noqa: BLE001 — граница системы, наружу ничего не летит
        return _fail(f"ошибка хранилища: {exc}")

    filtered = [
        t for t in tasks
        if t.get("priority") == priority and t.get("status") == status
    ]
    sliced = filtered[:limit]
    return json.dumps(
        {"status": "ok", "count": len(sliced), "items": sliced},
        ensure_ascii=False,
    )