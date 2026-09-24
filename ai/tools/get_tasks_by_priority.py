"""Tool: get_tasks_by_priority. Контракт (заглушка).

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

Краевые случаи:
    - неверный priority → ошибка;
    - limit <= 0 или limit > 50 → ошибка;
    - задач нет → успех, count: 0, items: [];
    - ошибка хранилища → _fail(...), без traceback наружу.
"""

from typing import Any


def run(input_data: dict[str, Any]) -> str:
    """Основная точка входа Tool.

    Args:
        input_data: входные параметры.

    Returns:
        JSON-строка с результатом.
    """
    raise NotImplementedError("Tool ещё не реализован")