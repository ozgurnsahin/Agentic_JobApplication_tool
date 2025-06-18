from crewai.tools import BaseTool
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
from duckduckgo_search import DDGS


class DuckDuckGoToolInput(BaseModel):
    query: str = Field(..., description="Search query for DuckDuckGo web search")
    max_results: int = Field(default=10, description="Maximum number of search results to return")
    region: str = Field(default="tr-tr", description="Search region (e.g., 'tr-tr' for Turkey, 'us-en' for US)")

class DuckDuckGoTool(BaseTool):
    name: str = "duckduckgo_search"
    description: str = (
        "Search the web using DuckDuckGo for job postings, company information, and general web content. "
        "Useful for finding job listings, company details, and industry information. "
        "Returns formatted search results with titles, URLs, and snippets."
    )
    args_schema: Type[BaseModel] = DuckDuckGoToolInput

    def _run(self, query: str, max_results: int = 10, region: str = "tr-tr") -> str:
        try:
            search_results = self.perform_search(query, max_results, region)
            
            if not search_results:
                return f"No search results found for query: '{query}'"
            
            formatted_results = self.format_search_results(search_results, query)
            
            return formatted_results
            
        except Exception as e:
            return f"Error performing DuckDuckGo search for '{query}': {str(e)}"
    
    def perform_search(self, query: str, max_results: int, region: str) -> List[Dict[str, Any]]:
        try:
                with DDGS() as ddgs:
                    # Perform text search
                    results = list(ddgs.text(
                        keywords=query,
                        max_results=max_results,
                        region=region,
                        safesearch='moderate',
                        timelimit=None  # No time limit
                    ))
                    
                    return results
        except Exception as e:
             print(f"DuckDuckGo search attempt failed: {e}")
    
    def format_search_results(self, results: List[Dict[str, Any]], query: str) -> str:
        if not results:
            return f"No results found for '{query}'"
        
        formatted_output = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            url = result.get('href', 'No URL')
            snippet = result.get('body', 'No description available')
            
            snippet = ' '.join(snippet.split())
            if len(snippet) > 200:
                snippet = snippet[:200] + "..."
            
            formatted_output.append(f"\n{i}. {title}")
            formatted_output.append(f"URL: {url}")
            formatted_output.append(f"Description: {snippet}")
            formatted_output.append("-" * 40)
        
        return "\n".join(formatted_output)