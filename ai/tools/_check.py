"""Проверка Tool get_tasks_by_priority без LLM."""

import json

from ai.tools.get_tasks_by_priority import run


def _parse(raw: str) -> dict:
    return json.loads(raw)


def main() -> None:
    # 1. Успех: high + todo, дефолтный limit
    res = _parse(run({"priority": "high"}))
    assert res["status"] == "ok", res
    assert res["count"] == 1, res  # только "Сделать отчёт"
    assert all(t["priority"] == "high" for t in res["items"]), res
    print("OK 1: high+todo →", res)

    # 2. Успех: medium + in_progress
    res = _parse(run({"priority": "medium", "status": "in_progress"}))
    assert res["status"] == "ok", res
    assert res["count"] == 1, res  # "Ревью PR"
    print("OK 2: medium+in_progress →", res)

    # 3. Успех: нет задач → count 0
    res = _parse(run({"priority": "low", "status": "done"}))
    assert res["status"] == "ok", res
    assert res["count"] == 0 and res["items"] == [], res
    print("OK 3: low+done →", res)

    # 4. Ошибка: неверный priority
    res = _parse(run({"priority": "urgent"}))
    assert res["status"] == "error", res
    assert "priority" in res["message"], res
    print("OK 4: urgent →", res)

    # 5. Ошибка: отсутствует priority
    res = _parse(run({}))
    assert res["status"] == "error", res
    print("OK 5: no priority →", res)

    # 6. Ошибка: неверный status
    res = _parse(run({"priority": "high", "status": "unknown"}))
    assert res["status"] == "error", res
    print("OK 6: bad status →", res)

    # 7. Ошибка: limit = 0
    res = _parse(run({"priority": "high", "limit": 0}))
    assert res["status"] == "error", res
    print("OK 7: limit=0 →", res)

    # 8. Ошибка: limit = 51
    res = _parse(run({"priority": "high", "limit": 51}))
    assert res["status"] == "error", res
    print("OK 8: limit=51 →", res)

    # 9. Ошибка: limit не число
    res = _parse(run({"priority": "high", "limit": "10"}))
    assert res["status"] == "error", res
    print("OK 9: limit='10' →", res)

    # 10. Успех: limit урезает
    res = _parse(run({"priority": "high", "status": "todo", "limit": 1}))
    assert res["status"] == "ok" and res["count"] <= 1, res
    print("OK 10: limit=1 →", res)

    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()