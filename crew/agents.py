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
    "model": "groq/openai/gpt-oss-20b",
    "api_key": get_groq_key(),
    "temperature": 0.2,
}

def create_scout_agent():
    return Agent(
        role="Opportunity Scout",
        goal=(
            "Find recent (last 30-60 days) construction project awards, tenders, and teaming "
            "opportunities in {country} that match the scope: {project_types}. "
            "Focus on MAIN CONTRACTOR AWARD ANNOUNCEMENTS and MAJOR TENDER PORTALS "
            "where subcontracting packages will be needed."
        ),
        backstory=(
            "You are a veteran construction market intelligence analyst in the Middle East. "
            "You know that a subcontractor finds work through main-contractor awards, "
            "not just government tenders. You scour MEED, Construction Week, Zawya Projects, "
            "Etimad, and news sources. You return raw snippets with source URLs."
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
            "Project Name, Client/Principal, Main Contractor (if any), Location, "
            "Estimated Value (or range), Project Date/Status, Source URL, and a brief scope summary. "
            "Return a clean JSON array. Mark value_type as OFFICIAL, ESTIMATED, or UNKNOWN."
        ),
        backstory=(
            "You are a meticulous data engineer. You never invent facts. If a field is missing, "
            "you mark it 'Not Disclosed'. You always include the source URL so the reader can verify."
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
            "Only include opportunities with a score of 4 or 5 in the final report. "
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
