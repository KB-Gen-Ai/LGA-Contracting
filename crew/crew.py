import os
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

def run_lead_generation_crew(country, project_types, min_value, max_results, recipients):
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

    recipient_list = [r.strip() for r in recipients.split(",") if r.strip()]
    send_email(
        recipients=recipient_list,
        subject=f"Daily Opportunity Brief - {country} - {project_types[:50]}...",
        html_body=str(result)
    )

    return str(result)
