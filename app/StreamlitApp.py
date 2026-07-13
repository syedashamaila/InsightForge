import os
import sys

PROJECT_ROOT = os.path.dirname(
os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    
import streamlit as st

from agents.orchestrator_agent import OrchestratorAgent


st.set_page_config(
    page_title="InsightForge",
    layout="wide"
)

st.title("InsightForge")
st.caption("AI Powered BI Requirement Analysis")


requirement = st.text_area(
    "Business Requirement",
    height=180,
    placeholder="Describe the dashboard you would like to build..."
)


if st.button("Generate Dashboard", type="primary"):

    if not requirement.strip():

        st.warning("Please enter a business requirement.")

        st.stop()

    orchestrator = OrchestratorAgent()

    with st.spinner("Running Multi-Agent Pipeline..."):

        result = orchestrator.run_pipeline(
            requirement
        )

    if result["status"] == "Failed":

        st.error(result["error"])

        st.stop()

    if result["status"] == "Needs Clarification":

        st.subheader("Clarification Required")

        clarification = result["clarification_result"]

        st.metric(
            "Confidence",
            clarification["confidence_score"]
        )

        for q in clarification["follow_up_questions"]:

            st.write("•", q)

        st.stop()


    st.header("Generated Dashboard")

    dashboard = result["dashboard_result"]

    figures = dashboard.get("figures", [])

    for visual in figures:

        st.subheader(
            visual["title"]
        )

        st.plotly_chart(
            visual["figure"],
            use_container_width=True
        )
