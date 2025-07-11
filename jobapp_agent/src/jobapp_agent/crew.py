from .db.database import CrewAIJobStorage
from .tools.job_database_tool import JobDatabaseTool
from .tools.pdf_generator_tool import PDFGeneratorTool

from typing import List
import os

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool, PGSearchTool, PDFSearchTool, FileReadTool

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
            date_format="%d-%m-%Y",
            max_iter=15,
            max_max_execution_time=3600,
            tools=[SerperDevTool(),
                   PGSearchTool(db_uri=db.connection_url,table_name='jobs'),
                   JobDatabaseTool(),
                   PDFSearchTool(pdf=cv_path)],
            respect_context_window=True
        )
        
    @agent
    def optimizer(self) -> Agent:
        db = CrewAIJobStorage()
        cv_path = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge", "ozgur_cv.pdf")
        cv_path = os.path.abspath(cv_path)
        
        return Agent(
            config=self.agents_config['optimizer'],
            verbose=True,
            inject_date=True,
            date_format="%d-%m-%Y",
            max_iter=15,
            max_max_execution_time=3600,
            tools=[PGSearchTool(db_uri=db.connection_url,table_name='jobs'),
                   JobDatabaseTool(),
                   FileReadTool(file_path=cv_path),
                   PDFGeneratorTool()],
            respect_context_window=True
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
        )
        
    @task
    def optimization_task(self) -> Task:
        return Task(
            config=self.tasks_config['optimization_task'],
            context=[self.research_task()],
        )


    @crew
    def crew(self) -> Crew:
        """Creates the JobappAgent crew"""

        return Crew(
            agents=[self.researcher(), self.optimizer()],
            tasks=[self.research_task(), self.optimization_task()],
            process=Process.sequential,
            verbose=True,
        )
