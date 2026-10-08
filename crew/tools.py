from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
from bs4 import BeautifulSoup


class WebSearchToolSchema(BaseModel):
    """Input schema for WebSearchTool."""
    query: str = Field(..., description="The search query.")


class WebSearchTool(BaseTool):
    name: str = "Web Search Tool"
    description: str = (
        "Searches the web using DuckDuckGo for a given query. Filters results "
        "to the past month. Returns top results with title, URL, and snippet."
    )
    args_schema: Type[BaseModel] = WebSearchToolSchema

    def _run(self, query: str) -> str:
        url = "https://html.duckduckgo.com/html/"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
            )
        }
        # df=m filters to past month, df=w to past week
        data = {"q": query, "df": "m"}
        try:
            resp = requests.post(url, data=data, headers=headers, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            results = []
            for i, result in enumerate(soup.select(".result")):
                if i >= 8:
                    break
                title_el = result.select_one(".result__a")
                snippet_el = result.select_one(".result__snippet")
                link_el = result.select_one(".result__url")
                date_el = result.select_one(".result__timestamp")
                title = title_el.get_text(strip=True) if title_el else "No Title"
                snippet = snippet_el.get_text(strip=True) if snippet_el else "No Snippet"
                link = link_el.get_text(strip=True) if link_el else "No URL"
                date = date_el.get_text(strip=True) if date_el else "No Date"
                results.append(
                    f"TITLE: {title}\nURL: {link}\nDATE: {date}\nSNIPPET: {snippet}\n"
                )
            if not results:
                return "No results found."
            return "\n---\n".join(results)
        except Exception as e:
            return f"Search failed: {str(e)}"


search_web_tool = WebSearchTool()
