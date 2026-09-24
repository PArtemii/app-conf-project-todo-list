"""Проверка Tool create_task без LLM."""

import json

from ai.tools.create_task import run


def _parse(raw: str) -> dict:
    return json.loads(raw)


def main() -> None:
    # 1. Успех: минимальный ввод
    res = _parse(run({"title": "Новая задача"}))
    assert res["status"] == "ok", res
    assert res["task"]["priority"] == "medium", res
    assert res["task"]["status"] == "todo", res
    print("OK 1:", res)

    # 2. Успех: все поля
    res = _parse(run({"title": "Важное", "priority": "high", "status": "in_progress"}))
    assert res["status"] == "ok", res
    assert res["task"]["priority"] == "high", res
    print("OK 2:", res)

    # 3. Ошибка: нет title
    res = _parse(run({}))
    assert res["status"] == "error", res
    print("OK 3:", res)

    # 4. Ошибка: пустой title
    res = _parse(run({"title": "   "}))
    assert res["status"] == "error", res
    print("OK 4:", res)

    # 5. Ошибка: title слишком длинный
    res = _parse(run({"title": "x" * 201}))
    assert res["status"] == "error", res
    print("OK 5:", res)

    # 6. Ошибка: неверный priority
    res = _parse(run({"title": "ok", "priority": "urgent"}))
    assert res["status"] == "error", res
    print("OK 6:", res)

    # 7. Ошибка: неверный status
    res = _parse(run({"title": "ok", "status": "unknown"}))
    assert res["status"] == "error", res
    print("OK 7:", res)

    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()