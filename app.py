import streamlit as st
from crew.crew import run_lead_generation_crew
import os

st.set_page_config(page_title="LGA - Lead Generation Agent", layout="wide")

st.title("🏗️ Lead Generation Agent")
st.markdown("Find, summarize, and grade construction opportunities matching your profile.")


def get_secret(key, default=""):
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


with st.form("lead_form"):
    st.subheader("🔍 Search Parameters")

    col1, col2 = st.columns(2)
    with col1:
        country = st.text_input("Country", value="Saudi Arabia")
        project_types = st.text_area(
            "Project Types / Scope Keywords",
            value=(
                "MEP, HVAC, Firefighting, Plumbing, Infrastructure, "
                "Water Networks, Metro, Airport, Hotels, Industrial Piping"
            ),
            height=80,
        )
    with col2:
        min_value = st.number_input(
            "Minimum Project Value (SAR)", value=5_000_000, step=1_000_000
        )
        max_results = st.slider("Max Results", min_value=5, max_value=30, value=15)

    recipients = st.text_input(
        "Recipient Emails (comma-separated)",
        value=get_secret("RECIPIENT_EMAILS", ""),
    )

    submitted = st.form_submit_button("🚀 Run Lead Generation", use_container_width=True)

if submitted:
    if not recipients:
        st.error("Please provide at least one recipient email.")
    else:
        with st.spinner("Agents are working... this may take a few minutes."):
            try:
                result = run_lead_generation_crew(
                    country=country,
                    project_types=project_types,
                    min_value=min_value,
                    max_results=max_results,
                    recipients=recipients,
                )
                st.success("✅ Leads generated and email sent!")
                with st.expander("📄 Full Report Preview"):
                    st.markdown(result, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.exception(e)
