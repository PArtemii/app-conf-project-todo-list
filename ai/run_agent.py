from crewai import Agent, Crew, Task
from ai.llm_factory import get_llm
from ai.tools.get_tasks_by_priority import get_tasks_by_priority
import sys
from ai.tools.code_tools import crewai_tools


agent = Agent(
    role="Ассистент todo-листа",
    goal=(
        "Отвечать на вопросы о коде бэкенда, опираясь только на ответы инструментов"
    ),
    backstory=(
        "Ты — ассистент проекта todo-list. Ты никогда не придумываешь задачи "
        "из головы: если пользователь спрашивает про задачи, ты сначала вызываешь "
        "инструмент get_tasks_by_priority и отвечаешь строго по его JSON-ответу. "
        "Если инструмент вернул ошибку — объясняешь пользователю, что именно "
        "не так с запросом, и предлагаешь допустимые значения."
        
        "Где определена функция или класс, ищешь через search_codebase с kind='symbol' "
        "по всему репозиторию, а код показываешь через read_file. "
        "Если инструмент вернул ошибку с hint, выполняешь hint; если ошибка осталась, "
        "говоришь о ней пользователю и не придумываешь результат."
    ),
    tools=[*crewai_tools()],
    llm=get_llm(),
    function_calling_llm=get_llm(),
    verbose=True,
    max_iter=5,
)

QUESTION = "Где в бэкенде определена функция health_check и что она возвращает? Покажи её код."

task = Task(
    description=sys.argv[1] if len(sys.argv) > 1 else QUESTION,
    expected_output="Короткий ответ на вопрос пользователя; если инструмент вернул ошибку — перескажи её",
    agent=agent,
)

crew = Crew(agents=[agent], tasks=[task], verbose=True)

if __name__ == "__main__":
    print(crew.kickoff())