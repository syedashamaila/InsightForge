import os
import sys

PROJECT_ROOT = os.path.dirname(
os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from dataclasses import asdict
from agents.clarification_agent import ClarificationAgent
from agents.requirement_agent import RequirementAgent
from agents.mockdata_agent import MockDataAgent
from agents.prototype_agent import PrototypeAgent
from agents.reporter_agent import ReporterAgent



def main():
    st.set_page_config(page_title="InsightsForge", layout="wide")
    st.title("InsightsForge")

    
    
    # Input section
    st.subheader("Input Business Requirement")
    user_requirement = st.text_area(
        "Enter your business requirement:",
        height=150,
        placeholder="Describe your business requirement here..."
    )
    
    # Button to run agents
    if st.button("Run Agents", type="primary"):
        if not user_requirement.strip():
            st.error("Please enter a business requirement")
            return
        
        clarified_req = None
        requirement_context = None
        
        # Clarification Agent Section
        try:
            with st.status("Running Clarification Agent...", expanded=True) as status:
                clarification_agent = ClarificationAgent()
                clarification_result = clarification_agent.run(user_requirement)
                clarified_req = clarification_result.clarified_requirement

                status.update(label="Clarification Agent Completed ✓", state="complete")
        except Exception as e:
            st.error(f"Clarification Agent Error: {str(e)}")
            return
        
        # Requirement Agent Section
        try:
            with st.status("Running Requirement Agent...", expanded=True) as status:
                requirement_agent = RequirementAgent()
                requirement_context = requirement_agent.analyze_requirement(clarified_req)
                status.update(label="Requirement Agent Completed ✓", state="complete")
        except Exception as e:
            st.error(f"Requirement Agent Error: {str(e)}")
            return
        
        # Mock Agents Section
        try:
            with st.status("Running MockData Agent...", expanded=True) as status:
                mock_agent = MockDataAgent(requirement_context)
                mock_output = mock_agent.generate_mock_data()
                status.update(label="MockData Agent Completed ✓", state="complete")
        except Exception as e:
            st.error(f"MockData Agent Error: {str(e)}")
            return

        # Prototype Agent Section
        try:
            with st.status("Running Prototype Agent...", expanded=True) as status:
                prototype_agent = PrototypeAgent()
                
                prototype = prototype_agent.create_prototype(
                    asdict(requirement_context) 
                    if hasattr(requirement_context, '__dataclass_fields__') 
                    else requirement_context,
                    asdict(clarified_req) 
                    if hasattr(clarified_req, '__dataclass_fields__') 
                    else clarified_req,
                    mock_output
                )
                status.update(label="Prototype Agent Completed ✓", state="complete")
        except Exception as e:
            st.error(f"Prototype Agent Error: {str(e)}")
            return

        # Reporter Agent Section
                
        try:
            with st.status("Running Reporter Agent...", expanded=True) as status:
                reporter_agent = ReporterAgent()
                dashboard = reporter_agent.generate_dashboard(prototype, mock_output)
                status.update(label="Reporter Agent Completed ✓", state="complete")
        except Exception as e:
            st.error(f"Reporter Agent Error: {str(e)}")
            return
        
        # Display Results
        st.subheader("Results")
        
        st.subheader("Clarification Agent Output")
        st.json(asdict(clarified_req) if hasattr(clarified_req, '__dataclass_fields__') else clarified_req)
        
        st.subheader("Requirement Agent Output")
        st.json(asdict(requirement_context) if hasattr(requirement_context, '__dataclass_fields__') else requirement_context)

        st.subheader("Mock Data Output")
        st.write(mock_output["metadata"])
        st.write(mock_output["data_dictionary"])

        for table_name, df in mock_output["dataframes"].items():
            st.subheader(f"Mock Data for {table_name}")
            st.dataframe(df)

        st.subheader("Prototype Agent Output")
        st.expander("View Prototype Output", expanded=True).json(prototype)

        st.subheader("Reporter Agent Output")
        st.subheader("Generated Dashboard")
        st.title(dashboard.get("dashboard_title", "Dashboard"))
        

        for visual in dashboard.get("figures", []):
           st.markdown(f"### {visual.get('title', visual.get('type', 'Visualization'))}")

           if visual.get("type", "") == "KPI Card":
               st.metric(
                   visual.get("title", ""),
                   visual.get("value", "")
               )
           elif visual.get("type", "") == "Table":
                st.dataframe(
                    visual.get("data", {}),
                    use_container_width=True
                )
           else:
               st.plotly_chart(
                   visual["figure"],
                   use_container_width=True,
                   key=visual["visual_id"]
               )
        
        
if __name__ == "__main__":
    main()
