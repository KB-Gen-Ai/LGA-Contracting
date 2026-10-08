from crewai.tools import BaseTool          # ← FIXED: was crewai_tools
from pydantic import BaseModel, Field      # ← FIXED: import BaseModel
from typing import Type
import requests
from bs4 import BeautifulSoup


class WebSearchToolSchema(BaseModel):      # ← FIXED: was (BaseTool)
    """Input schema for WebSearchTool."""
    query: str = Field(..., description="The search query.")


class WebSearchTool(BaseTool):
    name: str = "Web Search Tool"
    description: str = (
        "Searches the web using DuckDuckGo for a given query and returns "
        "top 5 results with snippets and URLs."
    )
    args_schema: Type[BaseModel] = WebSearchToolSchema   # ← type hint fixed

    def _run(self, query: str) -> str:
        url = "https://html.duckduckgo.com/html/"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        }
        try:
            resp = requests.post(url, data={"q": query}, headers=headers, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            results = []
            for i, result in enumerate(soup.select(".result")):
                if i >= 5:
                    break
                title_el = result.select_one(".result__a")
                snippet_el = result.select_one(".result__snippet")
                link_el = result.select_one(".result__url")
                title = title_el.get_text(strip=True) if title_el else "No Title"
                snippet = snippet_el.get_text(strip=True) if snippet_el else "No Snippet"
                link = link_el.get_text(strip=True) if link_el else "No URL"
                results.append(f"TITLE: {title}\nURL: {link}\nSNIPPET: {snippet}\n")
            if not results:
                return "No results found."
            return "\n---\n".join(results)
        except Exception as e:
            return f"Search failed: {str(e)}"


search_web_tool = WebSearchTool()
