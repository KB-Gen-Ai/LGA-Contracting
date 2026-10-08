from crewai import Task
from datetime import datetime, timedelta
from .agents import create_scout_agent, create_extractor_agent, create_scorer_agent


def create_scout_task(agent, country, project_types, min_value, max_results, days_back=90):
    today = datetime.utcnow().date()
    cutoff = today - timedelta(days=days_back)
    current_year = today.year
    current_month_year = today.strftime("%B %Y")

    return Task(
        description=(
            f"Today's date is {today.isoformat()}. "
            f"Find up to {max_results} construction opportunities in {country} "
            f"matching these scope keywords: {project_types}. "
            f"Minimum project value: SAR {min_value:,}.\n\n"
            f"STRICT RECENCY RULE: Only include opportunities PUBLISHED or ANNOUNCED "
            f"between {cutoff.isoformat()} and {today.isoformat()} (last {days_back} days). "
            f"Discard anything older. If you are not sure of the publication date, discard it.\n\n"
            f"For every result, you MUST report the publication date in ISO format "
            f"(YYYY-MM-DD) as shown on the source page. If the page does not show a date, "
            f"discard the result.\n\n"
            f"Run these searches (each separately):\n"
            f"- 'awarded contract {country} {current_month_year}'\n"
            f"- 'wins contract {country} {current_year}'\n"
            f"- 'main contractor selected {country} {current_year}'\n"
            f"- 'tender issued {country} {current_year}'\n"
            f"- plus each scope keyword combined with the current year.\n\n"
            f"Return raw findings. Every result MUST include: title, publication_date (ISO), "
            f"source_url, and snippet."
        ),
        expected_output=(
            f"A list of 10-20 raw snippets. Every item MUST have a publication_date "
            f"between {cutoff.isoformat()} and {today.isoformat()}. "
            f"Items without a verifiable date are dropped."
        ),
        agent=agent,
    )


def create_extractor_task(agent, context_task, days_back=30):
    today = datetime.utcnow().date()
    cutoff = today - timedelta(days=days_back)

    return Task(
        description=(
            f"Today is {today.isoformat()}. The acceptable publication window is "
            f"{cutoff.isoformat()} to {today.isoformat()}.\n\n"
            "From the Scout's output, extract structured data for each opportunity. "
            "Return a JSON array. Each item must have: "
            "project_name, principal, main_contractor, location, estimated_value, "
            "value_type (OFFICIAL/ESTIMATED/UNKNOWN), publication_date, source_url, "
            "source_title, verbatim_quote, scope_summary.\n\n"
            "CRITICAL RULES:\n"
            f"1. publication_date MUST be on or after {cutoff.isoformat()}. "
            "If the Scout did not provide a verifiable date, DROP the item.\n"
            "2. source_url MUST be copied verbatim from the Scout's output. Never invent a URL.\n"
            "3. verbatim_quote MUST be a direct quote (10-30 words) from the source that proves "
            "the opportunity exists.\n"
            "4. If a field is missing, set it to 'Not Disclosed'. Never invent a value.\n"
            "5. It is better to return 1 real, recent opportunity than 10 stale or fabricated ones."
        ),
        expected_output=(
            "A valid JSON array. Every item MUST have publication_date within the accepted window "
            "and a real source_url from the Scout's output."
        ),
        agent=agent,
        context=[context_task],
    )


def create_scorer_task(agent, context_task, profile_summary, days_back=30):
    today = datetime.utcnow().date()
    cutoff = today - timedelta(days=days_back)

    return Task(
        description=(
            f"Today is {today.isoformat()}. The acceptable publication window is "
            f"{cutoff.isoformat()} to {today.isoformat()}.\n\n"
            f"Using the extracted opportunities, score each on a 1-5 scale against this "
            f"company profile:\n{profile_summary}\n\n"
            f"For each opportunity with a score of 4 or 5, write a 2-3 sentence "
            f"'Why It Matches' rationale.\n\n"
            f"CRITICAL RULES:\n"
            f"1. Only include opportunities that have a real source_url, a verbatim_quote, "
            f"AND a publication_date within the accepted window.\n"
            f"2. If any of those three is missing or invalid, DROP the opportunity.\n"
            f"3. Every card MUST display 'Published: YYYY-MM-DD' immediately below the title.\n"
            f"4. The Source link must use the exact source_url from the extractor.\n"
            f"5. Immediately after the Source link, include the verbatim_quote in italics "
            f"so the client can see the evidence.\n"
            f"6. If zero opportunities pass the filter, return an HTML email with only the "
            f"header and the line: 'No verified opportunities matched in the last 30 days. "
            f"This is a normal outcome — quality over quantity.'\n\n"
            f"Return the final output as a clean, professional HTML email body with inline CSS. "
            f"Include: header with date, a summary line with total count, then each opportunity "
            f"as a card with Match Score, Published date, Value, Main Contractor, "
            f"Why It Matches, Source link, and Evidence quote."
        ),
        expected_output="A complete HTML string ready to be sent as an email.",
        agent=agent,
        context=[context_task],
    )
