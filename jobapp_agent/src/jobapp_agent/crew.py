from .db.database import CrewAIJobStorage
from .tools.job_database_tool import JobDatabaseTool 

from typing import List
import os

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool, PGSearchTool, PDFSearchTool

from dotenv import load_dotenv
load_dotenv()

@CrewBase
class JobappAgent():
    """JobappAgent crew"""
    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def researcher(self) -> Agent:
        db = CrewAIJobStorage()
        cv_path = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge", "ozgur_cv.pdf")
        cv_path = os.path.abspath(cv_path)
        
        return Agent(
            config=self.agents_config['researcher'],
            verbose=True,
            inject_date=True,
            reasoning=True,
            date_format="%d-%m-%Y",
            max_reasoning_attempts=3,
            max_iter=10,
            max_max_execution_time=3600,
            tools=[SerperDevTool(country="Turkey", n_results=15),
                   PGSearchTool(db_uri=db.connection_url,table_name='jobs'),
                   JobDatabaseTool(),
                   PDFSearchTool(pdf=cv_path)],
            respect_context_window=True
        )


    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
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
