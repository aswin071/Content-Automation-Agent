from tabnanny import verbose
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from content_ai_agent.tools.youtube_api import YouTubeTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

# @CrewBase
# class ContentAiAgent():
#     """ContentAiAgent crew"""

#     agents: List[BaseAgent]
#     tasks: List[Task]

#     # Learn more about YAML configuration files here:
#     # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
#     # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
#     # If you would like to add tools to your agents, you can learn more about it here:
#     # https://docs.crewai.com/concepts/agents#agent-tools
#     @agent
#     def researcher(self) -> Agent:
#         return Agent(
#             config=self.agents_config['researcher'], # type: ignore[index]
#             verbose=True
#         )

#     @agent
#     def reporting_analyst(self) -> Agent:
#         return Agent(
#             config=self.agents_config['reporting_analyst'], # type: ignore[index]
#             verbose=True
#         )

#     # To learn more about structured task outputs,
#     # task dependencies, and task callbacks, check out the documentation:
#     # https://docs.crewai.com/concepts/tasks#overview-of-a-task
#     @task
#     def research_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['research_task'], # type: ignore[index]
#         )

#     @task
#     def reporting_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['reporting_task'], # type: ignore[index]
#             output_file='report.md'
#         )

#     @crew
#     def crew(self) -> Crew:
#         """Creates the ContentAiAgent crew"""
#         # To learn how to add knowledge sources to your crew, check out the documentation:
#         # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

#         return Crew(
#             agents=self.agents, # Automatically created by the @agent decorator
#             tasks=self.tasks, # Automatically created by the @task decorator
#             process=Process.sequential,
#             verbose=True,
#             # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
#         )



@CrewBase
class ContentAiAgent():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # ===== AGENTS =====
    @agent
    def topic_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['topic_finder'],
            tools=[YouTubeTool()],  # Add YouTubeTool(), SerpAPITool() later
            verbose=True
        )

    @agent
    def content_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['content_researcher'],
            tools=[],  # Add WebSearchTool() later
            verbose=True
        )

    @agent
    def script_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['script_writer'],
            tools=[],  # No tools needed - uses LLM directly
            verbose=True
        )

    # ===== TASKS =====
    @task
    def find_trending_topics(self) -> Task:
        return Task(config=self.tasks_config['find_trending_topics'])

    @task
    def research_content(self) -> Task:
        return Task(config=self.tasks_config['research_content'])

    @task
    def write_script(self) -> Task:
        return Task(
            config=self.tasks_config['write_script'],
            output_file='script.md'  # Final output
        )

    # ===== CREW =====
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # Auto-collected from @agent decorators
            tasks=self.tasks,    # Auto-collected from @task decorators
            process=Process.sequential,  # Run in order
            verbose=True
        )