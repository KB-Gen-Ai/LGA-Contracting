import os
from crew.crew import run_lead_generation_crew

def main():
    country = os.getenv("LGA_COUNTRY", "Saudi Arabia")
    project_types = os.getenv(
        "LGA_PROJECT_TYPES",
        "MEP, HVAC, Firefighting, Plumbing, Infrastructure, Water Networks, Metro, Airport, Hotels, Industrial Piping"
    )
    min_value = int(os.getenv("LGA_MIN_VALUE", 5_000_000))
    max_results = int(os.getenv("LGA_MAX_RESULTS", 15))
    recipients = os.getenv("RECIPIENT_EMAILS", "")

    if not recipients:
        raise ValueError("RECIPIENT_EMAILS environment variable is not set.")

    print(f"Running LGA for {country}...")
    result = run_lead_generation_crew(
        country=country,
        project_types=project_types,
        min_value=min_value,
        max_results=max_results,
        recipients=recipients
    )
    print("LGA run complete.")
    print(result[:500])  # Print a preview

if __name__ == "__main__":
    main()
