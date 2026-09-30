from ai.tools.get_tasks_by_priority import get_tasks_by_priority

print("name:", get_tasks_by_priority.name)
print("ok :", get_tasks_by_priority.run(priority="high", status="todo"))
print("err:", get_tasks_by_priority.run(priority="urgent"))