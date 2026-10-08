import os
import re
import requests
from datetime import datetime, timedelta
from crewai import Crew, Process
from .agents import create_scout_agent, create_extractor_agent, create_scorer_agent
from .tasks import create_scout_task, create_extractor_task, create_scorer_task
from utils.emailer import send_email, get_secret


ZOOM_PROFILE_SUMMARY = """
Zoom Al Arab General Contracting Co. is a Saudi-based MEP and infrastructure subcontractor.
Core scope: MEP, HVAC/VRF, chilled water networks, firefighting systems, plumbing,
electrical distribution, low current, water treatment, industrial piping.
Sectors: Metro, airports, hotels/hospitality, universities, defense facilities,
research centers, industrial plants (cement, power), ports/terminals.
Geography: Riyadh, Jeddah, KAEC, Yanbu, Jubail, Eastern Province, AlUla, Al Jouf.
Typical clients: Main contractors (CEMFA, SML Sembol, Zamil, FMC, Drake & Scull, Emaar)
and industrial operators (SABIC, ARAMCO).
Past projects include: Riyadh Metro, Rixos Jeddah, Bay La Sun Hotel, SAMI Al Kharj,
KAPSARC, AlUla HHBH, KAIA immigration systems, Al Jouf University infrastructure.
"""


def validate_urls_in_html(html: str) -> str:
    """Replace <a> links that don't return HTTP 200 with a warning."""
    def replace_link(match):
        url = match.group(1)
        try:
            r = requests.head(
                url, timeout=5, allow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            if r.status_code == 200:
                return match.group(0)
            return (
                '<span style="color:#c0392b;">'
                '[Source link unavailable — verify manually]</span>'
            )
        except Exception:
            return (
                '<span style="color:#c0392b;">'
                '[Source link unavailable — verify manually]</span>'
            )

    return re.sub(
        r'<a\s+href="([^"]+)"[^>]*>.*?</a>',
        replace_link,
        html,
        flags=re.DOTALL,
    )


def flag_stale_dates(html: str, cutoff: datetime.date) -> str:
    """Highlight any YYYY-MM-DD date in the HTML older than cutoff."""
    pattern = re.compile(r'(\d{4})-(\d{2})-(\d{2})')

    def check(match):
        try:
            d = datetime.strptime(match.group(0), "%Y-%m-%d").date()
            if d < cutoff:
                return f'<span style="color:#c0392b;">[STALE: {match.group(0)}]</span>'
            return match.group(0)
        except ValueError:
            return match.group(0)

    return pattern.sub(check, html)


def run_lead_generation_crew(country, project_types, min_value, max_results, recipients):
    cutoff = datetime.utcnow().date() - timedelta(days=30)

    scout = create_scout_agent()
    extractor = create_extractor_agent()
    scorer = create_scorer_agent()

    scout_task = create_scout_task(scout, country, project_types, min_value, max_results)
    extractor_task = create_extractor_task(extractor, scout_task)
    scorer_task = create_scorer_task(scorer, extractor_task, ZOOM_PROFILE_SUMMARY)

    crew = Crew(
        agents=[scout, extractor, scorer],
        tasks=[scout_task, extractor_task, scorer_task],
        process=Process.sequential,
        verbose=True,
        memory=False,
    )

    result = crew.kickoff()
    html_body = str(result)

    # Diagnostic — printed to Streamlit Cloud logs
    found_dates = re.findall(r'\d{4}-\d{2}-\d{2}', html_body)
    print(f"Dates found in output: {found_dates}")
    print(f"Cutoff: {cutoff}")

    # Safety net 1 — flag stale dates
    html_body = flag_stale_dates(html_body, cutoff)

    # Safety net 2 — validate links
    html_body = validate_urls_in_html(html_body)

    recipient_list = [r.strip() for r in recipients.split(",") if r.strip()]
    send_email(
        recipients=recipient_list,
        subject=f"Daily Opportunity Brief - {country}",
        html_body=html_body,
    )

    return html_body
