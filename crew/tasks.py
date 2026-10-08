from crewai import Task
from .agents import create_scout_agent, create_extractor_agent, create_scorer_agent

def create_scout_task(agent, country, project_types, min_value, max_results):
    return Task(
        description=(
            f"Find up to {max_results} recent construction opportunities in {country} "
            f"matching these scope keywords: {project_types}. "
            f"Minimum project value: SAR {min_value:,}. "
            f"Focus on MAIN CONTRACTOR AWARD ANNOUNCEMENTS and major project news from the last 30-60 days. "
            f"Search for phrases like 'awarded contract Saudi Arabia', 'wins contract KSA', "
            f"'main contractor selected', 'tender issued', 'RFQ issued' combined with the scope keywords. "
            f"Use the web search tool. Return raw findings with source URLs."
        ),
        expected_output=(
            "A list of 10-20 raw snippets, each containing a project title, a short description, "
            "and the source URL."
        ),
        agent=agent,
    )

def create_extractor_task(agent, context_task):
    return Task(
        description=(
            "From the raw snippets provided by the Scout, extract structured data for each opportunity. "
            "Return a JSON array. Each item must have: "
            "project_name, principal, main_contractor, location, estimated_value, value_type (OFFICIAL/ESTIMATED/UNKNOWN), "
            "project_date, source_url, scope_summary. "
            "If a field is not available, set it to 'Not Disclosed'."
        ),
        expected_output="A valid JSON array of opportunity objects.",
        agent=agent,
        context=[context_task],
    )

def create_scorer_task(agent, context_task, profile_summary):
    return Task(
        description=(
            f"Using the extracted opportunities, score each on a 1-5 scale against this company profile: "
            f"{profile_summary}. "
            f"For each opportunity with a score of 4 or 5, write a 2-3 sentence 'Why It Matches' rationale. "
            f"Only keep opportunities scored 4 or 5. "
            f"Return the final output as a clean, professional HTML email body. "
            f"Use inline CSS for styling. Include: header with date, a summary line, "
            f"then each opportunity as a card with Match Score, Value, Main Contractor, "
            f"Why It Matches, and Source link."
        ),
        expected_output="A complete HTML string ready to be sent as an email.",
        agent=agent,
        context=[context_task],
    )
