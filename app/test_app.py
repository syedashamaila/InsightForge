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



def main():
    st.set_page_config(page_title="Agent Tester", layout="wide")
    st.title("Clarification and Requirement Agent Tester")
    
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
        mock_agent = MockDataAgent(requirement_context)
        mock_output = mock_agent.generate_mock_data()

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


if __name__ == "__main__":
    main()
