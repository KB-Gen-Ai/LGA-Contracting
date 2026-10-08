import crewai.llms.cache as _crewai_cache
_crewai_cache.mark_cache_breakpoint = lambda msg: msg

from crewai import Agent
from crewai_tools import FirecrawlScrapeWebsiteTool
from .tools import search_web_tool
import os


def get_groq_key():
    try:
        import streamlit as st
        return st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    except Exception:
        return os.getenv("GROQ_API_KEY")


llm_config = {
    "model": "groq/openai\\/gpt-oss-120b",
    "api_key": get_groq_key(),
    "temperature": 0.2,
}


def create_scout_agent():
    return Agent(
        role="Opportunity Scout",
        goal=(
            "Find recent construction project awards, tenders, and teaming "
            "opportunities in {country} that match the scope: {project_types}. "
            "Focus on MAIN CONTRACTOR AWARD ANNOUNCEMENTS and MAJOR TENDER PORTALS "
            "where subcontracting packages will be needed. "
            "Only return opportunities PUBLISHED in the last 30 days."
        ),
        backstory=(
            "You are a veteran construction market intelligence analyst in the Middle East. "
            "You know that a subcontractor finds work through main-contractor awards, "
            "not just government tenders. You scour MEED, Construction Week, Zawya Projects, "
            "Etimad, and news sources. You ONLY return recent items and you always "
            "record the publication date. If you cannot verify the date, you discard the item."
        ),
        tools=[search_web_tool, FirecrawlScrapeWebsiteTool()],
        llm=llm_config,
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )


def create_extractor_agent():
    return Agent(
        role="Data Extractor",
        goal=(
            "From the raw snippets provided, extract for EACH opportunity: "
            "project_name, principal, main_contractor, location, estimated_value, "
            "value_type (OFFICIAL/ESTIMATED/UNKNOWN), publication_date, source_url, "
            "source_title, verbatim_quote, scope_summary. "
            "Return a clean JSON array. DROP any opportunity older than 30 days. "
            "DROP any opportunity without a real source URL."
        ),
        backstory=(
            "You are a meticulous data engineer. You never invent facts. If a field is "
            "missing, you mark it 'Not Disclosed'. If a date is missing or older than "
            "30 days, you drop the item entirely. You always include the source URL "
            "verbatim so the reader can verify."
        ),
        tools=[],
        llm=llm_config,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )


def create_scorer_agent():
    return Agent(
        role="Fit Scorer & Rationale Writer",
        goal=(
            "For EACH extracted opportunity, score the match against the company profile "
            "on a scale of 1-5. Provide a 'Why It Matches' rationale with specific evidence. "
            "Only include opportunities with a score of 4 or 5. "
            "Every card must display the publication date. "
            "Format the final output as a professional HTML email digest."
        ),
        backstory=(
            "You are the business development director for a Saudi MEP and infrastructure "
            "subcontractor. You know exactly what a good lead looks like. You are concise, "
            "evidence-based, and you never overstate. Your output is sent directly to the client."
        ),
        tools=[],
        llm=llm_config,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )
