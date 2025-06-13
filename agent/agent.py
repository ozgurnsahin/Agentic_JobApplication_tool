from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.webtools import WebTools
from agno.tools.crawl4ai import Crawl4aiTools
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv
load_dotenv()

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[Crawl4aiTools(max_length=None)], show_tool_calls=True
)

agent.print_response("Search web page: 'https://www.linkedin.com/jobs/view/4248402141'", markdown=True)
