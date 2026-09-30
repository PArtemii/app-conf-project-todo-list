from crewai import Agent, Crew, Task

from ai.llm_factory import get_llm
from ai.tools.get_tasks_by_priority import get_tasks_by_priority


agent = Agent(
    role="Ассистент todo-листа",
    goal=(
        "Помогать пользователю находить задачи по приоритету и статусу, "
        "отвечая только на основе данных из инструмента."
    ),
    backstory=(
        "Ты — ассистент проекта todo-list. Ты никогда не придумываешь задачи "
        "из головы: если пользователь спрашивает про задачи, ты сначала вызываешь "
        "инструмент get_tasks_by_priority и отвечаешь строго по его JSON-ответу. "
        "Если инструмент вернул ошибку — объясняешь пользователю, что именно "
        "не так с запросом, и предлагаешь допустимые значения."
    ),
    tools=[get_tasks_by_priority],
    llm=get_llm(),
    function_calling_llm=get_llm(),
    verbose=True,
    max_iter=5,
)

task = Task(
    description=(
        "Найди мои задачи с приоритетом high и статусом todo. "
        "Для этого ты ОБЯЗАН вызвать инструмент get_tasks_by_priority. "
        "ВАЖНО: не выводи вызов инструмента текстом и не пиши JSON в ответ. "
        "Просто вызови инструмент и дождись его результата. "
        "Затем напиши пользователю обычным текстом список найденных задач "
        "или сообщение, что задач с такими параметрами нет."
        "Ты никогда не пишешь JSON в ответ пользователю. "
        "Если нужно получить данные — ты вызываешь инструмент через function calling, "
        "а пользователю отвечаешь обычным текстом."
    ),
    expected_output=(
        "Обычный текст: список задач (id, title, priority, status) "
        "или фраза, что задач с такими параметрами нет. Без JSON."
    ),
    agent=agent,
)

crew = Crew(agents=[agent], tasks=[task], verbose=True)

if __name__ == "__main__":
    print(crew.kickoff())