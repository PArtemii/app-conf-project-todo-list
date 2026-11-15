
"""Запуск команды CrewAI из агентов Developer и Reviewer."""

from crewai import Agent, Crew, Process, Task

from ai.llm_factory import get_llm
from ai.tools.code_tools import crewai_tools as code_tools
from ai.tools.generated_files import crewai_tools as generated_tools
from ai.tools.rag_pipeline import crewai_tools as docs_tools


def create_developer(llm):
    """Создаёт агента, который изучает проект и генерирует тесты."""
    tools = [
        *code_tools(),
        *docs_tools(),
        *generated_tools(),
    ]

    return Agent(
        role="Developer",
        goal=(
            "Изучать код и документацию проекта и создавать "
            "качественные Python-тесты только в каталоге generated/"
        ),

    backstory=(
        "Ты опытный Python-разработчик, который создаёт реальные файлы тестов. "
        "Сначала изучи исходный код через read_file и search_codebase, "
        "при необходимости используй search_docs. "
        "Затем ОБЯЗАТЕЛЬНО вызови инструмент write_generated, "
        "передав path='generated/test_health_check.py' "
        "и content с полным Python-кодом тестов. "
        "Просто показать код в ответе недостаточно: "
        "файл должен физически существовать на диске. "
        "Не используй заглушки pass и фиктивные проверки. "
        "Если write_generated вернул ошибку, сообщи о ней честно. "
        "Не утверждай, что файл создан, пока не получишь "
        "от write_generated ответ со статусом ok. "
        "Не изменяй исходные файлы приложения."
    ),

        tools=tools,
        llm=llm,
        function_calling_llm=llm,
        verbose=True,
        max_iter=15,
        allow_delegation=False,
    )


def create_reviewer(llm):
    """Создаёт агента для проверки сгенерированных тестов."""
    tools = [
        *code_tools(),
        *docs_tools(),
    ]

    return Agent(
        role="Reviewer",
        goal=(
            "Проверять качество сгенерированных Python-тестов, "
            "их соответствие коду проекта и результаты Ruff"
        ),
        backstory=(
            "Ты опытный Python-разработчик и ревьюер. "
            "Ты внимательно изучаешь файлы, созданные Developer, "
            "проверяешь корректность тестов и запускаешь линтер. "
            "Ты не изменяешь файлы и не создаёшь новые. "
            "В итоговом отчёте указываешь найденные ошибки, "
            "результаты проверок и рекомендации."
        ),
        tools=tools,
        llm=llm,
        function_calling_llm=llm,
        verbose=True,
        max_iter=6,
        allow_delegation=False,
    )


def create_tasks(developer, reviewer):
    """Создаёт две последовательные задачи для команды."""

    development_task = Task(
        description=(
            "Изучи реализацию health_check в проекте. "
            "Найди соответствующий исходный код и документацию. "
            "Обязательно прочитай main.py со строки 30 до конца функции "
            "health_check, включая все варианты возвращаемого ответа. "
            "Подготовь три настоящих pytest-теста: успешное подключение "
            "к базе данных, отсутствие DATABASE_URL и ошибка подключения. "
            "Используй unittest.mock для изоляции базы данных. "
            "После подготовки кода обязательно вызови write_generated "
            "с path='generated/test_health_check.py' и полным кодом в content. "
            "Не завершай задачу до получения status='ok' от инструмента. "
            "Не используй pass или фиктивные проверки. "
            "Создай файл generated/test_health_check.py "
            "с тестами для этой функции. "
            "Для записи используй только инструмент write_generated. "
            "Не изменяй существующие файлы проекта. "
            "В ответе перечисли созданные файлы."
        ),
        expected_output=(
            "Файл generated/test_health_check.py с корректными "
            "pytest-тестами и краткое описание результата."
        ),
        agent=developer,
    )

    review_task = Task(
        description=(
            "Проверь результат предыдущей задачи Developer. "
            "Прочитай созданный файл generated/test_health_check.py, "
            "сравни тесты с реализацией health_check и запусти Ruff. "
            "Если файл отсутствует или инструмент вернул ошибку, "
            "явно сообщи об этом. "
            "Не создавай и не изменяй файлы."
        ),
        expected_output=(
            "Отчёт Reviewer: проверенные файлы, результаты Ruff, "
            "найденные проблемы и итоговое заключение."
        ),
        agent=reviewer,
        context=[development_task],
    )

    return [development_task, review_task]


def create_crew():
    """Создаёт команду из двух агентов с последовательными задачами."""
    llm = get_llm()

    developer = create_developer(llm)
    reviewer = create_reviewer(llm)

    tasks = create_tasks(developer, reviewer)

    return Crew(
        agents=[developer, reviewer],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
        memory=False,
    )


def main():
    """Запускает команду Developer → Reviewer."""
    crew = create_crew()
    result = crew.kickoff()

    print("\n=== РЕЗУЛЬТАТ РАБОТЫ CREW ===")
    print(result)


if __name__ == "__main__":
    main()
