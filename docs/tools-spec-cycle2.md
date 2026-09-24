# Спецификации Tool — цикл 2

## Tool 1: get_tasks_by_priority

- **Назначение:** возвращает задачи с указанным приоритетом. Использовать, когда пользователь спрашивает о задачах по приоритету.
- **Вход (`input_data`):**
  - `priority`: `str` — обязателен, одно из `'high'`, `'medium'`, `'low'`.
  - `status`: `str` — необязателен, одно из `'todo'`, `'in_progress'`, `'done'`, по умолчанию `'todo'`.
  - `limit`: `int` — необязателен, диапазон `1..50`, по умолчанию `10`.
- **Выход:** JSON-строка.
  - Успех: `{"status": "ok", "count": 0, "items": []}`
  - Ошибка: `{"status": "error", "message": "priority должен быть 'high', 'medium' или 'low', получено 'urgent'"}`
- **Краевые случаи:**
  - неверный `priority` → ошибка;
  - неверный `status` → ошибка;
  - `limit <= 0` или `limit > 50` → ошибка;
  - `limit` не целое число → ошибка;
  - задач нет → успех, `count: 0`, `items: []`;
  - ошибка хранилища → `{"status": "error"}`, без traceback наружу.
- **Пример вызова:**
  ```python
  from ai.tools.get_tasks_by_priority import run
  run({"priority": "high", "status": "todo", "limit": 5})
  ```

## Tool 2: create_task

- **Назначение:** создаёт новую задачу. Использовать, когда пользователь просит добавить задачу в список.
- **Вход (`input_data`):**
  - `title`: `str` — обязателен, непустой, длина `1..200`.
  - `priority`: `str` — необязателен, одно из `'high'`, `'medium'`, `'low'`, по умолчанию `'medium'`.
  - `status`: `str` — необязателен, одно из `'todo'`, `'in_progress'`, `'done'`, по умолчанию `'todo'`.
- **Выход:** JSON-строка.
  - Успех: `{"status": "ok", "task": {"id": 8, "title": "Новая задача", "priority": "medium", "status": "todo"}}`
  - Ошибка: `{"status": "error", "message": "title обязателен и должен быть непустой строкой"}`
- **Краевые случаи:**
  - нет `title` или он пустой/не строка → ошибка;
  - `title` длиннее 200 символов → ошибка;
  - неверный `priority` → ошибка;
  - неверный `status` → ошибка;
  - ошибка хранилища → `{"status": "error"}`, без traceback наружу.
- **Пример вызова:**
  ```python
  from ai.tools.create_task import run
  run({"title": "Купить хлеб", "priority": "low"})
  ```