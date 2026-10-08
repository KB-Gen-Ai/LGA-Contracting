from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
from bs4 import BeautifulSoup


class WebSearchToolSchema(BaseModel):
    query: str = Field(..., description="The search query.")


class WebSearchTool(BaseTool):
    name: str = "Web Search Tool"
    description: str = (
        "Searches the web using DuckDuckGo. Returns up to 5 results with "
        "title, URL, and snippet."
    )
    args_schema: Type[BaseModel] = WebSearchToolSchema

    def _run(self, query: str) -> str:
        results = self._ddg_html(query)
        if not results:
            results = self._ddg_lite(query)
        if not results:
            return (
                f"SEARCH FAILED for query: {query}. "
                f"No results from DuckDuckGo. Try a different query."
            )
        return "\n---\n".join(results)

    def _ddg_html(self, query):
        url = "https://html.duckduckgo.com/html/"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
        data = {"q": query}
        try:
            resp = requests.post(url, data=data, headers=headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            out = []
            for i, result in enumerate(soup.select(".result")):
                if i >= 5:
                    break
                title_el = result.select_one(".result__a")
                snippet_el = result.select_one(".result__snippet")
                link_el = result.select_one(".result__url")
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                link = link_el.get_text(strip=True) if link_el else ""
                out.append(f"TITLE: {title}\nURL: {link}\nSNIPPET: {snippet}\n")
            return out
        except Exception as e:
            print(f"[search] _ddg_html failed: {e}")
            return []

    def _ddg_lite(self, query):
        url = "https://lite.duckduckgo.com/lite/"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }
        data = {"q": query}
        try:
            resp = requests.post(url, data=data, headers=headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            out = []
            links = soup.select("a.result-link")
            snippets = soup.select("td.result-snippet")
            for i, link in enumerate(links):
                if i >= 5:
                    break
                title = link.get_text(strip=True)
                href = link.get("href", "")
                snippet = snippets[i].get_text(strip=True) if i < len(snippets) else ""
                out.append(f"TITLE: {title}\nURL: {href}\nSNIPPET: {snippet}\n")
            return out
        except Exception as e:
            print(f"[search] _ddg_lite failed: {e}")
            return []


search_web_tool = WebSearchTool()
