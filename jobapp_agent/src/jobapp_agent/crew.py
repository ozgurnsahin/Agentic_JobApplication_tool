from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool
from typing import List
from dotenv import load_dotenv

load_dotenv()

@CrewBase
class JobappAgent():
    """JobappAgent crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            verbose=True,
            inject_date=True,
            reasoning=True,
            date_format="%d-%m-%Y",
            max_reasoning_attempts=2,
            max_iter=5,
            max_max_execution_time=1800,
            tools=[SerperDevTool(country="Turkey", n_results=15)]
        )


    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )


    @crew
    def crew(self) -> Crew:
        """Creates the JobappAgent crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
