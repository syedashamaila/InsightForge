import os
import sys
PROJECT_ROOT = os.path.dirname(
os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

print("PROJECT_ROOT", PROJECT_ROOT)
print("PATH:", sys.path)

from agents import orchestrator_agent

print("CWD", os.getcwd())
print("PATH:")
for p in sys.path:
    print(p)


"""
InsightForge – Multi-Agent BI Requirement Analysis Platform

A production-grade Streamlit application with professional dashboard layout
inspired by Microsoft Fabric/Azure AI Studio. Three-column layout: compact header,
fixed left navigation, central workflow area, and right audit panel.

Architecture:
- Pure presentation layer (no business logic)
- State management via Streamlit session_state
- Professional light theme with blue accents
- Compact, minimal spacing design
- Three-column responsive dashboard layout
"""

import streamlit as st
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import pandas as pd
import plotly.express as px




# Configure page
st.set_page_config(
    page_title="InsightForge – BI Requirement Analysis",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CUSTOM CSS - MODERN ENTERPRISE THEME
# ============================================================================

def apply_custom_css() -> None:
    """Apply Microsoft enterprise-grade theme with premium styling."""
    st.markdown("""
    <style>
    /* Root Variables - Microsoft Office Color Palette */
    :root {
        --primary-color: #0078d4;
        --primary-light: #107c10;
        --primary-dark: #005a9e;
        --secondary-color: #f3f2f1;
        --bg-main: #fafafa;
        --bg-card: #ffffff;
        --bg-hover: #f7f7f7;
        --bg-header: #f7f7f7;
        --text-primary: #242424;
        --text-secondary: #595959;
        --text-tertiary: #8a8a8a;
        --border-color: #e1e1e1;
        --success: #107c10;
        --warning: #ffb900;
        --error: #d83b01;
        --info: #0078d4;
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
        --shadow-md: 0 2px 8px rgba(0, 0, 0, 0.12);
        --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.15);
    }

    /* Global Styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    html, body {
        background: var(--bg-main);
        color: var(--text-primary);
        font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
        font-size: 14px;
        line-height: 1.5;
    }

    /* Main Layout */
    .main {
        background: var(--bg-main);
        padding: 0 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid var(--border-color);
        width: 300px !important;
        box-shadow: 1px 0 3px rgba(0, 0, 0, 0.06);
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding: 28px 20px !important;
    }

    /* Sidebar Text */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: var(--text-primary) !important;
    }

    /* Cards and Containers */
    .stCard, [data-testid="stVerticalBlock"] > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.2s ease !important;
        padding: 0 !important;
    }

    .stCard:hover {
        border-color: var(--primary-color) !important;
        box-shadow: var(--shadow-md) !important;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, rgba(0, 82, 204, 0.08), transparent) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        padding: 16px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
    }

    .streamlit-expanderHeader:hover {
        background: linear-gradient(90deg, rgba(0, 82, 204, 0.12), transparent) !important;
        border-color: var(--primary-light) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .streamlit-expander {
        background: transparent !important;
        border: none !important;
    }

    /* Buttons */
    .stButton > button {
        background: var(--primary-color) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        box-shadow: var(--shadow-sm) !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        cursor: pointer !important;
    }

    .stButton > button:hover {
        background: var(--primary-dark) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Text Input */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 12px 14px !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(0, 82, 204, 0.08) !important;
        background: var(--bg-main) !important;
    }

    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, rgba(0, 82, 204, 0.08) 0%, rgba(0, 82, 204, 0.04) 100%);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-sm);
    }

    .kpi-card:hover {
        background: linear-gradient(135deg, rgba(0, 82, 204, 0.12) 0%, rgba(0, 82, 204, 0.06) 100%);
        border-color: var(--primary-color);
        box-shadow: var(--shadow-md);
    }

    .kpi-value {
        font-size: 32px;
        font-weight: 700;
        color: var(--primary-color);
        margin: 12px 0 8px 0;
    }

    .kpi-label {
        font-size: 13px;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }

    /* Metric */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: capitalize;
        letter-spacing: 0;
        margin: 4px 4px 4px 0;
        transition: all 0.3s ease;
        border: 1px solid;
    }

    .badge-success {
        background: rgba(15, 143, 71, 0.1);
        color: #0f8f47;
        border-color: rgba(15, 143, 71, 0.2);
    }

    .badge-warning {
        background: rgba(217, 119, 6, 0.1);
        color: #d97706;
        border-color: rgba(217, 119, 6, 0.2);
    }

    .badge-error {
        background: rgba(211, 47, 47, 0.1);
        color: #d32f2f;
        border-color: rgba(211, 47, 47, 0.2);
    }

    .badge-info {
        background: rgba(0, 82, 204, 0.1);
        color: #0052cc;
        border-color: rgba(0, 82, 204, 0.2);
    }

    /* Workflow Progress */
    .workflow-stage {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 16px;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }

    .workflow-stage.completed {
        background: rgba(15, 143, 71, 0.08);
        border-color: rgba(15, 143, 71, 0.2);
    }

    .workflow-stage.current {
        background: rgba(0, 82, 204, 0.1);
        border-color: var(--primary-color);
        border-left: 4px solid var(--primary-color);
        box-shadow: var(--shadow-sm);
    }

    .workflow-stage.pending {
        background: var(--bg-card);
        border-color: var(--border-color);
        opacity: 0.5;
    }

    .stage-icon {
        font-size: 22px;
        flex-shrink: 0;
    }

    .stage-label {
        font-weight: 600;
        flex: 1;
        color: var(--text-primary);
        font-size: 14px;
    }

    .stage-status {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        color: var(--text-secondary);
    }

    /* Dividers */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 24px 0 !important;
    }

    /* Hero Header */
    .hero-section {
        background: linear-gradient(135deg, #f0f4ff 0%, #e8eeff 100%);
        border: none;
        border-radius: 0;
        padding: 80px 48px;
        text-align: center;
        margin-bottom: 0;
        box-shadow: none;
        margin-left: -16px;
        margin-right: -16px;
        margin-top: -16px;
    }

    .hero-icon {
        font-size: 64px;
        margin-bottom: 24px;
        display: block;
    }

    .hero-title {
        font-size: 64px;
        font-weight: 800;
        background: linear-gradient(135deg, #000000 0%, #0078d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 8px;
        letter-spacing: -1px;
    }

    .hero-title-accent {
        color: #0078d4;
    }

    .hero-subtitle {
        font-size: 24px;
        color: var(--text-secondary);
        margin-bottom: 16px;
        font-weight: 600;
    }

    .hero-description {
        font-size: 16px;
        color: var(--text-secondary);
        max-width: 800px;
        margin: 0 auto;
        line-height: 1.8;
    }

    /* Error Cards */
    .error-card {
        background: rgba(211, 47, 47, 0.08);
        border: 1px solid rgba(211, 47, 47, 0.2);
        border-radius: 12px;
        padding: 16px;
        border-left: 4px solid #d32f2f;
        margin: 16px 0;
    }

    .error-title {
        font-weight: 700;
        margin-bottom: 8px;
        color: #d32f2f;
        font-size: 14px;
    }

    .error-message {
        font-size: 14px;
        line-height: 1.5;
        color: var(--text-primary);
    }

    /* Success Cards */
    .success-card {
        background: rgba(15, 143, 71, 0.08);
        border: 1px solid rgba(15, 143, 71, 0.2);
        border-radius: 12px;
        padding: 16px;
        border-left: 4px solid #0f8f47;
        margin: 16px 0;
    }

    .success-title {
        font-weight: 700;
        margin-bottom: 8px;
        color: #0f8f47;
        font-size: 14px;
    }

    .success-message {
        font-size: 14px;
        line-height: 1.5;
        color: var(--text-primary);
    }

    /* Audit Trail */
    .audit-timeline {
        position: relative;
        padding: 0;
    }

    .audit-event {
        background: var(--bg-card);
        border-left: 3px solid var(--primary-color);
        border-radius: 10px;
        padding: 14px;
        margin: 12px 0;
        font-size: 13px;
        transition: all 0.3s ease;
        position: relative;
        padding-left: 18px;
    }

    .audit-event::before {
        content: '';
        position: absolute;
        left: -10px;
        top: 50%;
        transform: translateY(-50%);
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: var(--primary-color);
        border: 3px solid var(--bg-main);
    }

    .audit-event:hover {
        background: var(--bg-hover);
        box-shadow: var(--shadow-sm);
    }

    .audit-timestamp {
        color: var(--text-tertiary);
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }

    .audit-agent {
        color: var(--primary-color);
        font-weight: 700;
        margin: 6px 0 4px 0;
        font-size: 14px;
    }

    .audit-action {
        color: var(--text-primary);
        margin: 4px 0;
        font-size: 13px;
    }

    /* Requirements Card */
    .requirement-card {
        background: linear-gradient(135deg, rgba(0, 82, 204, 0.08) 0%, rgba(0, 82, 204, 0.04) 100%);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 24px;
        box-shadow: var(--shadow-sm);
    }

    .requirement-title {
        font-size: 18px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 8px;
    }

    .requirement-description {
        font-size: 14px;
        color: var(--text-secondary);
        margin-bottom: 16px;
        line-height: 1.6;
    }

    /* Dashboard Grid */
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }

    .dashboard-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-sm);
    }

    .dashboard-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }

    /* Feature Cards */
    .feature-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 28px 24px;
        text-align: center;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }

    .feature-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-4px);
    }

    .feature-icon {
        font-size: 40px;
        margin-bottom: 16px;
        display: block;
    }

    .feature-title {
        font-size: 16px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 12px;
    }

    .feature-description {
        font-size: 13px;
        color: var(--text-secondary);
        line-height: 1.6;
    }

    /* Responsive */
    @media (max-width: 1024px) {
        .hero-section {
            padding: 40px 24px;
        }

        .hero-title {
            font-size: 40px;
        }

        .hero-subtitle {
            font-size: 18px;
        }
    }

    @media (max-width: 768px) {
        .hero-title {
            font-size: 32px;
        }

        .hero-subtitle {
            font-size: 16px;
        }
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(0, 82, 204, 0.04);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(0, 82, 204, 0.2);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 82, 204, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session() -> None:
    """Initialize Streamlit session state with default values."""
    defaults = {
        "business_requirement": "",
        "workflow_started": False,
        "current_stage": "idle",
        "orchestrator_results": None,
        "audit_trail": [],
        "error_message": None,
        "success_message": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_session() -> None:
    """Reset entire session state."""
    st.session_state.business_requirement = ""
    st.session_state.workflow_started = False
    st.session_state.current_stage = "idle"
    st.session_state.orchestrator_results = None
    st.session_state.audit_trail = []
    st.session_state.error_message = None
    st.session_state.success_message = None
    logger.info("Session state reset")


def add_audit_event(agent_name: str, action: str, status: str, reason: str = "") -> None:
    """Add event to audit trail."""
    event = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "action": action,
        "status": status,
        "reason": reason,
    }
    st.session_state.audit_trail.insert(0, event)


def set_error(message: str) -> None:
    """Set error message."""
    st.session_state.error_message = message
    logger.error(message)


def set_success(message: str) -> None:
    """Set success message."""
    st.session_state.success_message = message
    logger.info(message)


# ============================================================================
# HEADER SECTION
# ============================================================================

def render_header() -> None:
    """Render compact header section."""
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #d9d9d9;">
        <div>
            <div style="font-size: 16px; font-weight: 700; color: #1a1a1a;">🔷 InsightForge</div>
            <div style="font-size: 12px; color: #595959; margin-top: 2px;">BI Requirement Analysis</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# SIDEBAR SECTION
# ============================================================================

def render_sidebar() -> None:
    """Render compact left navigation sidebar."""
    with st.sidebar:
        st.markdown("🔷 InsightForge", unsafe_allow_html=True)
        st.divider()
        
        st.markdown("**Business Requirement**")
        requirement = st.text_area(
            "Requirement:",
            value=st.session_state.business_requirement,
            height=100,
            placeholder="Example: Power BI Executive Sales Dashboard...",
            key="requirement_input",
            label_visibility="collapsed"
        )
        st.session_state.business_requirement = requirement

        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Start", use_container_width=True, key="start_btn"):
                if not st.session_state.business_requirement.strip():
                    set_error("Please enter a requirement")
                else:
                    try:
                        st.session_state.workflow_started = True
                        st.session_state.current_stage = "requirements"
                        add_audit_event("System", "Workflow Started", "initiated")


                        import os
                        import sys

                        st.write(os.getcwd())
                        st.write(sys.path)


                        # Instantiate OrchestratorAgent and run pipeline
                        from agents import orchestrator_agent
                        orchestrator = orchestrator_agent.OrchestratorAgent()
                        
                        st.session_state.orchestrator_results = orchestrator.run_pipeline(st.session_state.business_requirement)
                        
                        result = st.session_state.orchestrator_results
                        if result.get("status") == "Success":
                            st.session_state.current_stage = "completed"
                        else:
                            st.session_state.current_stage = "requirements"
                            #set_error("Pipeline failed. Please check the logs for details.")

                        add_audit_event("OrchestratorAgent", "Pipeline Completed", "completed")
                        set_success("Analysis completed!")
                        st.rerun()
                    except Exception as e:
                        set_error(f"Pipeline error: {str(e)}")
                        logger.exception("Pipeline execution failed")

        with col2:
            if st.button("🔄 Reset", use_container_width=True, key="reset_btn"):
                reset_session()
                set_success("Workflow reset")

        st.divider()
        st.markdown("**Status**")
        
        status_map = {
            "idle": ("🔴", "Not Started"),
            "requirements": ("🟡", "Requirements"),
            "clarification": ("🟡", "Clarification"),
            "prototype": ("🟡", "Prototype"),
            "reporter": ("🟢", "Report"),
            "completed": ("🟢", "Completed"),
        }
        status_color, status_text = status_map.get(st.session_state.current_stage, ("🔴", "Unknown"))
        st.write(f"{status_color} {status_text}")


# ============================================================================
# PROGRESS TRACKER
# ============================================================================

def render_progress() -> None:
    """Render compact workflow progress tracker."""
    st.markdown("**Workflow Progress**")

    stages = [
        ("requirements", "Requirements", "📋"),
        ("clarification", "Clarification", "❓"),
        ("prototype", "Prototype", "🎨"),
        ("reporter", "Reporter", "📊"),
        ("completed", "Completed", "✅"),
    ]

    for stage_id, stage_name, icon in stages:
        if st.session_state.current_stage == stage_id:
            css_class = "current"
        elif stage_id in ["requirements", "clarification", "prototype", "reporter"]:
            if st.session_state.current_stage in ["clarification", "prototype", "reporter", "completed"]:
                if (stage_id == "requirements" or
                    (stage_id == "clarification" and st.session_state.current_stage in ["prototype", "reporter", "completed"]) or
                    (stage_id == "prototype" and st.session_state.current_stage in ["reporter", "completed"])):
                    css_class = "completed"
                else:
                    css_class = "pending"
            else:
                css_class = "pending"
        else:
            css_class = "pending"

        st.markdown(f"""
        <div class="workflow-stage {css_class}">
            <div class="stage-icon">{icon}</div>
            <div class="stage-label">{stage_name}</div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================================
# REQUIREMENT PANEL
# ============================================================================

def render_requirement_panel() -> None:
    """Render requirement analysis panel."""
    if not st.session_state.orchestrator_results:
        return
    
    requirement_result = st.session_state.orchestrator_results.get("requirement_result")
    if not requirement_result:
        return

    with st.expander("📋 **Requirement Analysis**", expanded=True):
        result = requirement_result

        if isinstance(result, dict):
            # Business Objective
            if "business_objective" in result:
                st.markdown("#### Business Objective")
                st.info(result["business_objective"])

            # Key Metrics
            if "kpis" in result and result["kpis"]:
                st.markdown("#### 📊 Key Performance Indicators")
                cols = st.columns(3)
                
                for idx, kpi in enumerate(result["kpis"]):
                    with cols[idx % len(cols)]:
                       st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">{kpi.get('name', 'KPI')}</div>
                            <div class="metric-value">{kpi.get('target', 'N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                    
            # Measures
            if "measures" in result and result["measures"]:
                st.markdown("#### 📈 Measures")
                for measure in result["measures"]:
                    st.markdown(f"<span class='badge badge-info'>{measure}</span>",
                              unsafe_allow_html=True)

            # Dimensions
            if "dimensions" in result and result["dimensions"]:
                st.markdown("#### 🏷️ Dimensions")
                for dimension in result["dimensions"]:
                    st.markdown(f"<span class='badge badge-info'>{dimension}</span>",
                              unsafe_allow_html=True)

            # Filters
            if "filters" in result and result["filters"]:
                st.markdown("#### 🔍 Filters")
                for filter_item in result["filters"]:
                    st.markdown(f"<span class='badge badge-warning'>{filter_item}</span>",
                              unsafe_allow_html=True)

            # Assumptions
            if "assumptions" in result and result["assumptions"]:
                st.markdown("#### 💡 Assumptions")
                for assumption in result["assumptions"]:
                    st.write(f"• {assumption}")

            # Dependencies
            if "dependencies" in result and result["dependencies"]:
                st.markdown("#### 🔗 Dependencies")
                for dep in result["dependencies"]:
                    st.write(f"• {dep}")

            # Risks
            if "risks" in result and result["risks"]:
                st.markdown("#### ⚠️ Risks")
                for risk in result["risks"]:
                    st.markdown(f"<span class='badge badge-error'>{risk}</span>",
                              unsafe_allow_html=True)


# ============================================================================
# CLARIFICATION PANEL
# ============================================================================

def render_clarification_panel() -> None:
    """Render clarification panel."""
    if not st.session_state.orchestrator_results:
        return
    
    clarification_result = st.session_state.orchestrator_results.get("clarification_result")
    if not clarification_result:
        return

    with st.expander("❓ **Clarification Analysis**", expanded=True):
        result = clarification_result

        if isinstance(result, dict):
            # Readiness Score
            if "readiness_score" in result:
                score = result["readiness_score"]
                st.markdown("#### Readiness Score")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Overall Readiness</div>
                        <div class="metric-value">{score}%</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Recommendation
            if "recommendation" in result:
                st.markdown("#### Recommendation")
                if result["recommendation"].lower() == "proceed":
                    st.success(result["recommendation"])
                else:
                    st.warning(result["recommendation"])

            # Clarification Questions
            if "questions" in result and result["questions"]:
                st.markdown("#### Clarification Questions")
                for idx, question in enumerate(result["questions"], 1):
                    st.write(f"**Q{idx}:** {question}")

            # Business Risks
            if "business_risks" in result and result["business_risks"]:
                st.markdown("#### Business Risks")
                for risk in result["business_risks"]:
                    st.markdown(f"<span class='badge badge-error'>{risk}</span>",
                              unsafe_allow_html=True)

            # Confidence
            if "confidence" in result:
                st.markdown("#### Confidence Level")
                st.info(f"{result['confidence']}%")

            # Assumptions
            if "assumptions" in result and result["assumptions"]:
                st.markdown("#### Assumptions")
                for assumption in result["assumptions"]:
                    st.write(f"• {assumption}")


# ============================================================================
# PROTOTYPE PANEL
# ============================================================================

def render_prototype_panel() -> None:
    """Render prototype analysis panel with dashboard preview."""
    if not st.session_state.orchestrator_results:
        return
    
    prototype_result = st.session_state.orchestrator_results.get("prototype_result")
    if not prototype_result:
        return

    with st.expander("🎨 **Dashboard Prototype**", expanded=True):
        result = prototype_result

        if isinstance(result, dict):
            # Dashboard Title
            st.info("This prototype was automatically generated from the approved requirements and clarification responses. It is a starting point for development and may require further refinement.")
            if "dashboard_title" in result:
                st.markdown(f"#### {result['dashboard_title']}")
            
            # Version and Created Date
            col1, col2 = st.columns(2)
            with col1:
                if "version" in result:
                    st.write(f"**Version:** {result['version']}")
            with col2:
                if "created_date" in result:
                    st.write(f"**Created:** {result['created_date']}")
            
            st.markdown("---")
            
            # Pages
            if "Pages" in result and result["Pages"]:
                st.markdown("#### 📄 Pages")
                for page in result["Pages"]:
                    st.write(f"• {page}")
            
            st.markdown("---")
            
            # Convert Sample Data to DataFrame
            df = None
            if "Sample_data" in result and result["Sample_data"]:
                try:
                    if isinstance(result["Sample_data"], dict):
                        df = pd.DataFrame(result["Sample_data"])
                    elif isinstance(result["Sample_data"], list):
                        df = pd.DataFrame(result["Sample_data"])
                    else:
                        df = pd.DataFrame(result["Sample_data"])
                except Exception:
                    df = None
            
            # Render Filters and Slicers
            if ("Filters" in result and result["Filters"]) or ("Slicers" in result and result["Slicers"]):
                st.markdown("#### 🔍 Dashboard Filters & Slicers")
                filter_cols = st.columns(3)
                filter_idx = 0
                
                # Render Filters
                if "Filters" in result and result["Filters"]:
                    for filter_item in result["Filters"]:
                        if isinstance(filter_item, dict):
                            filter_name = filter_item.get("name", "Filter")
                            filter_type = filter_item.get("type", "text")
                            with filter_cols[filter_idx % 3]:
                                if filter_type.lower() == "date":
                                    st.date_input(f"📅 {filter_name}")
                                elif filter_type.lower() == "multi":
                                    st.multiselect(f"🔹 {filter_name}", ["Option 1", "Option 2", "Option 3"])
                                else:
                                    st.selectbox(f"🔹 {filter_name}", ["Select...", "Option 1", "Option 2", "Option 3"])
                                filter_idx += 1
                        else:
                            with filter_cols[filter_idx % 3]:
                                st.selectbox(f"🔹 Filter", ["Select...", "Option 1", "Option 2"])
                                filter_idx += 1
                
                # Render Slicers
                if "Slicers" in result and result["Slicers"]:
                    for slicer in result["Slicers"]:
                        if isinstance(slicer, dict):
                            slicer_name = slicer.get("name", "Slicer")
                            slicer_type = slicer.get("type", "single")
                            with filter_cols[filter_idx % 3]:
                                if slicer_type.lower() == "multi":
                                    st.multiselect(f"📌 {slicer_name}", ["Option 1", "Option 2", "Option 3"])
                                else:
                                    st.selectbox(f"📌 {slicer_name}", ["Select...", "Option 1", "Option 2", "Option 3"])
                                filter_idx += 1
                        else:
                            with filter_cols[filter_idx % 3]:
                                st.selectbox(f"📌 Slicer", ["Select...", "Option 1", "Option 2"])
                                filter_idx += 1
                
                st.markdown("---")
            
            # Render KPI Cards
            if "KPI_cards" in result and result["KPI_cards"]:
                st.markdown("#### 🎯 KPI Cards")
                kpi_cols = st.columns(len(result["KPI_cards"]))
                
                for idx, kpi in enumerate(result["KPI_cards"]):
                    with kpi_cols[idx]:
                        if isinstance(kpi, dict):
                            kpi_title = kpi.get("title", "KPI")
                            kpi_value = kpi.get("value", "N/A")
                            kpi_delta = kpi.get("delta", None)
                            st.metric(kpi_title, kpi_value, delta=kpi_delta)
                        else:
                            kpi_str = str(kpi)
                            if " - " in kpi_str:
                                parts = kpi_str.split(" - ")
                                st.metric(parts[0], parts[1] if len(parts) > 1 else "N/A")
                            else:
                                st.metric("KPI", kpi_str)
                
                st.markdown("---")
            
            # Render Visuals - Power BI style layout
            if "Visuals" in result and result["Visuals"]:
                st.markdown("## 📊 Dashboard Visuals")
                
                visuals_list = result["Visuals"]
                chart_visuals = []
                table_visuals = []
                
                # Separate charts from tables
                for visual in visuals_list:
                    if isinstance(visual, dict):
                        visual_type = visual.get("type", "").lower()
                        if visual_type == "table":
                            table_visuals.append(visual)
                        else:
                            chart_visuals.append(visual)
                    else:
                        chart_visuals.append(visual)
                
                # Render charts in two-column grid
                if chart_visuals:
                    for idx in range(0, len(chart_visuals), 2):
                        cols = st.columns(2)
                        
                        # First chart in pair
                        with cols[0]:
                            visual = chart_visuals[idx]
                            if isinstance(visual, dict):
                                visual_type = visual.get("type", "").lower()
                                visual_title = visual.get("title", "Chart")
                                visual_config = visual.get("config", {})
                                
                                try:
                                    if visual_type == "column chart" or visual_type == "bar chart":
                                        if df is not None and not df.empty:
                                            x_col = visual_config.get("x_axis", df.columns[0] if len(df.columns) > 0 else None)
                                            y_col = visual_config.get("y_axis", df.columns[1] if len(df.columns) > 1 else None)
                                            if x_col and y_col and x_col in df.columns and y_col in df.columns:
                                                fig = px.bar(df, x=x_col, y=y_col, title=visual_title)
                                                st.plotly_chart(fig, use_container_width=True)
                                            else:
                                                st.info("📊 Chart preview (data configuration pending)")
                                        else:
                                            st.info("📊 Bar chart (sample data not available)")
                                    
                                    elif visual_type == "line chart":
                                        if df is not None and not df.empty:
                                            x_col = visual_config.get("x_axis", df.columns[0] if len(df.columns) > 0 else None)
                                            y_col = visual_config.get("y_axis", df.columns[1] if len(df.columns) > 1 else None)
                                            if x_col and y_col and x_col in df.columns and y_col in df.columns:
                                                fig = px.line(df, x=x_col, y=y_col, title=visual_title)
                                                st.plotly_chart(fig, use_container_width=True)
                                            else:
                                                st.info("📈 Line chart preview (data configuration pending)")
                                        else:
                                            st.info("📈 Line chart (sample data not available)")
                                    
                                    elif visual_type == "pie chart":
                                        if df is not None and not df.empty:
                                            label_col = visual_config.get("labels", df.columns[0] if len(df.columns) > 0 else None)
                                            value_col = visual_config.get("values", df.columns[1] if len(df.columns) > 1 else None)
                                            if label_col and value_col and label_col in df.columns and value_col in df.columns:
                                                fig = px.pie(df, names=label_col, values=value_col, title=visual_title)
                                                st.plotly_chart(fig, use_container_width=True)
                                            else:
                                                st.info("🥧 Pie chart preview (data configuration pending)")
                                        else:
                                            st.info("🥧 Pie chart (sample data not available)")
                                    
                                    elif visual_type == "scatter":
                                        if df is not None and not df.empty:
                                            x_col = visual_config.get("x_axis", df.columns[0] if len(df.columns) > 0 else None)
                                            y_col = visual_config.get("y_axis", df.columns[1] if len(df.columns) > 1 else None)
                                            if x_col and y_col and x_col in df.columns and y_col in df.columns:
                                                fig = px.scatter(df, x=x_col, y=y_col, title=visual_title)
                                                st.plotly_chart(fig, use_container_width=True)
                                            else:
                                                st.info("⚫ Scatter plot preview (data configuration pending)")
                                        else:
                                            st.info("⚫ Scatter plot (sample data not available)")
                                    
                                    elif visual_type == "treemap":
                                        if df is not None and not df.empty:
                                            labels_col = visual_config.get("labels", df.columns[0] if len(df.columns) > 0 else None)
                                            values_col = visual_config.get("values", df.columns[1] if len(df.columns) > 1 else None)
                                            if labels_col and values_col and labels_col in df.columns and values_col in df.columns:
                                                fig = px.treemap(df, labels=labels_col, values=values_col, title=visual_title)
                                                st.plotly_chart(fig, use_container_width=True)
                                            else:
                                                st.info("🌳 Treemap preview (data configuration pending)")
                                        else:
                                            st.info("🌳 Treemap (sample data not available)")
                                    
                                    elif visual_type == "kpi card":
                                        kpi_title = visual_config.get("title", "KPI")
                                        kpi_value = visual_config.get("value", "N/A")
                                        kpi_delta = visual_config.get("delta", None)
                                        st.metric(kpi_title, kpi_value, delta=kpi_delta)
                                    
                                    else:
                                        st.info(f"📊 {visual_title} ({visual_type})")
                                
                                except Exception as e:
                                    st.warning(f"⚠️ Could not render {visual_title}: {str(e)}")
                            else:
                                st.write(f"• {visual}")
                        
                        # Second chart in pair (if exists)
                        if idx + 1 < len(chart_visuals):
                            with cols[1]:
                                visual = chart_visuals[idx + 1]
                                if isinstance(visual, dict):
                                    visual_type = visual.get("type", "").lower()
                                    visual_title = visual.get("title", "Chart")
                                    visual_config = visual.get("config", {})
                                    
                                    try:
                                        if visual_type == "column chart" or visual_type == "bar chart":
                                            if df is not None and not df.empty:
                                                x_col = visual_config.get("x_axis", df.columns[0] if len(df.columns) > 0 else None)
                                                y_col = visual_config.get("y_axis", df.columns[1] if len(df.columns) > 1 else None)
                                                if x_col and y_col and x_col in df.columns and y_col in df.columns:
                                                    fig = px.bar(df, x=x_col, y=y_col, title=visual_title)
                                                    st.plotly_chart(fig, use_container_width=True)
                                                else:
                                                    st.info("📊 Chart preview (data configuration pending)")
                                            else:
                                                st.info("📊 Bar chart (sample data not available)")
                                        
                                        elif visual_type == "line chart":
                                            if df is not None and not df.empty:
                                                x_col = visual_config.get("x_axis", df.columns[0] if len(df.columns) > 0 else None)
                                                y_col = visual_config.get("y_axis", df.columns[1] if len(df.columns) > 1 else None)
                                                if x_col and y_col and x_col in df.columns and y_col in df.columns:
                                                    fig = px.line(df, x=x_col, y=y_col, title=visual_title)
                                                    st.plotly_chart(fig, use_container_width=True)
                                                else:
                                                    st.info("📈 Line chart preview (data configuration pending)")
                                            else:
                                                st.info("📈 Line chart (sample data not available)")
                                        
                                        elif visual_type == "pie chart":
                                            if df is not None and not df.empty:
                                                label_col = visual_config.get("labels", df.columns[0] if len(df.columns) > 0 else None)
                                                value_col = visual_config.get("values", df.columns[1] if len(df.columns) > 1 else None)
                                                if label_col and value_col and label_col in df.columns and value_col in df.columns:
                                                    fig = px.pie(df, names=label_col, values=value_col, title=visual_title)
                                                    st.plotly_chart(fig, use_container_width=True)
                                                else:
                                                    st.info("🥧 Pie chart preview (data configuration pending)")
                                            else:
                                                st.info("🥧 Pie chart (sample data not available)")
                                        
                                        elif visual_type == "scatter":
                                            if df is not None and not df.empty:
                                                x_col = visual_config.get("x_axis", df.columns[0] if len(df.columns) > 0 else None)
                                                y_col = visual_config.get("y_axis", df.columns[1] if len(df.columns) > 1 else None)
                                                if x_col and y_col and x_col in df.columns and y_col in df.columns:
                                                    fig = px.scatter(df, x=x_col, y=y_col, title=visual_title)
                                                    st.plotly_chart(fig, use_container_width=True)
                                                else:
                                                    st.info("⚫ Scatter plot preview (data configuration pending)")
                                            else:
                                                st.info("⚫ Scatter plot (sample data not available)")
                                        
                                        elif visual_type == "treemap":
                                            if df is not None and not df.empty:
                                                labels_col = visual_config.get("labels", df.columns[0] if len(df.columns) > 0 else None)
                                                values_col = visual_config.get("values", df.columns[1] if len(df.columns) > 1 else None)
                                                if labels_col and values_col and labels_col in df.columns and values_col in df.columns:
                                                    fig = px.treemap(df, labels=labels_col, values=values_col, title=visual_title)
                                                    st.plotly_chart(fig, use_container_width=True)
                                                else:
                                                    st.info("🌳 Treemap preview (data configuration pending)")
                                            else:
                                                st.info("🌳 Treemap (sample data not available)")
                                        
                                        elif visual_type == "kpi card":
                                            kpi_title = visual_config.get("title", "KPI")
                                            kpi_value = visual_config.get("value", "N/A")
                                            kpi_delta = visual_config.get("delta", None)
                                            st.metric(kpi_title, kpi_value, delta=kpi_delta)
                                        
                                        else:
                                            st.info(f"📊 {visual_title} ({visual_type})")
                                    
                                    except Exception as e:
                                        st.warning(f"⚠️ Could not render {visual_title}: {str(e)}")
                                else:
                                    st.write(f"• {visual}")
                
                st.markdown("---")
            
            # Render Mock Tables
            if "Mock_tables" in result and result["Mock_tables"]:
                st.markdown("#### 📋 Mock Tables")
                for idx, table in enumerate(result["Mock_tables"]):
                    if isinstance(table, dict):
                        table_name = table.get("name", f"Table {idx + 1}")
                        table_data = table.get("data", {})
                        with st.expander(f"📋 {table_name}", expanded=False):
                            try:
                                table_df = pd.DataFrame(table_data)
                                st.dataframe(table_df, use_container_width=True)
                            except Exception:
                                st.write(table_data)
                    else:
                        with st.expander(f"📋 Table {idx + 1}", expanded=False):
                            st.write(table)
                
                st.markdown("---")
            
            # Color Rules
            if "color_rules" in result and result["color_rules"]:
                st.markdown("#### 🎨 Color Rules")
                with st.expander("🎨 Color Rules Detail", expanded=False):
                    color_rules_data = []
                    for rule in result["color_rules"]:
                        if isinstance(rule, dict):
                            color_rules_data.append(rule)
                        else:
                            color_rules_data.append({"Rule": str(rule)})
                    if color_rules_data:
                        try:
                            st.dataframe(pd.DataFrame(color_rules_data), use_container_width=True)
                        except Exception:
                            for rule in result["color_rules"]:
                                st.write(f"• {rule}")
                
                st.markdown("---")
            
            # Client Review Notes
            if "Client_review_notes" in result and result["Client_review_notes"]:
                st.markdown("#### 📝 Client Review Notes")
                if isinstance(result["Client_review_notes"], list):
                    for note in result["Client_review_notes"]:
                        st.write(f"• {note}")
                else:
                    st.write(result["Client_review_notes"])
            
            # Next Steps
            if "Next_Steps" in result and result["Next_Steps"]:
                st.markdown("#### 📌 Next Steps")
                if isinstance(result["Next_Steps"], list):
                    for step in result["Next_Steps"]:
                        st.write(f"• {step}")
                else:
                    st.write(result["Next_Steps"])
            
            # Ready for Development
            if "Ready_for_development" in result:
                st.markdown("---")
                if result["Ready_for_development"]:
                    st.success("✅ Ready for Development")
                else:
                    st.warning("⚠️ Not Yet Ready for Development")
            
            st.markdown("---")
            
            # Approve Button
            if st.button("✅ Approve Prototype", use_container_width=True):
                st.session_state.current_stage = "reporter"
                add_audit_event("User", "Prototype Approved", "approved")
                set_success("Prototype approved!")
                st.rerun()


# ============================================================================
# REPORT PANEL
# ============================================================================

def render_report_panel() -> None:
    """Render report panel with comprehensive report sections and download functionality."""
    if not st.session_state.orchestrator_results:
        return
    
    report_result = st.session_state.orchestrator_results.get("report_result")
    if not report_result:
        return

    with st.expander("📊 **Executive Report**", expanded=True):
        result = report_result

        if isinstance(result, dict):
            # Display report sections in specified order
            
            # 1. Executive Summary
            if "executive_summary" in result and result["executive_summary"]:
                st.markdown("#### 📋 Executive Summary")
                st.info(result["executive_summary"])
            
            # 2. Requirement Summary
            if "requirement_summary" in result and result["requirement_summary"]:
                st.markdown("#### 📊 Requirement Summary")
                req_summary = result["requirement_summary"]
                if isinstance(req_summary, list):
                    for item in req_summary:
                        st.write(f"• {item}")
                else:
                    st.write(req_summary)
            
            # 3. Clarification Summary
            if "clarification_summary" in result and result["clarification_summary"]:
                st.markdown("#### ❓ Clarification Summary")
                clarif_summary = result["clarification_summary"]
                if isinstance(clarif_summary, list):
                    for item in clarif_summary:
                        st.write(f"• {item}")
                else:
                    st.write(clarif_summary)
            
            # 4. Prototype Summary
            if "prototype_summary" in result and result["prototype_summary"]:
                st.markdown("#### 🎨 Prototype Summary")
                proto_summary = result["prototype_summary"]
                if isinstance(proto_summary, list):
                    for item in proto_summary:
                        st.write(f"• {item}")
                else:
                    st.write(proto_summary)
            
            # 5. Recommendations
            if "recommendations" in result and result["recommendations"]:
                st.markdown("#### 🎯 Recommendations")
                recommendations = result["recommendations"]
                if isinstance(recommendations, list):
                    for idx, rec in enumerate(recommendations, 1):
                        st.write(f"{idx}. {rec}")
                else:
                    st.write(recommendations)
            
            # 6. Implementation Notes
            if "implementation_notes" in result and result["implementation_notes"]:
                st.markdown("#### 📝 Implementation Notes")
                impl_notes = result["implementation_notes"]
                if isinstance(impl_notes, list):
                    for idx, note in enumerate(impl_notes, 1):
                        st.write(f"{idx}. {note}")
                else:
                    st.write(impl_notes)
            
            # 7. Risks & Assumptions
            if "risks_and_assumptions" in result and result["risks_and_assumptions"]:
                st.markdown("#### ⚠️ Risks & Assumptions")
                risks = result["risks_and_assumptions"]
                if isinstance(risks, list):
                    for item in risks:
                        st.write(f"• {item}")
                else:
                    st.write(risks)
            
            # Report Preview Section
            st.markdown("---")
            st.markdown("#### 📄 Report Preview")
            
            report_path = result.get("report_path")
            if report_path:
                try:
                    report_file = Path(report_path)
                    if report_file.exists() and report_file.suffix.lower() == ".html":
                        try:
                            with open(report_file, "r", encoding="utf-8") as f:
                                html_content = f.read()
                            import streamlit.components.v1 as components
                            components.html(html_content, height=800, scrolling=True)
                        except Exception as e:
                            st.warning(f"Could not read HTML report: {str(e)}")
                    else:
                        st.info("📋 HTML report file not yet available.")
                except Exception as e:
                    st.warning(f"Error accessing report: {str(e)}")
            else:
                st.info("📋 No report file path available.")
            
            # Download Section
            st.markdown("---")
            st.markdown("#### 📥 Download Report")

            col1, col2 = st.columns(2)

            # HTML Download Button
            with col1:
                if report_path:
                    try:
                        report_file = Path(report_path)
                        if report_file.exists() and report_file.suffix.lower() == ".html":
                            with open(report_file, "rb") as f:
                                html_bytes = f.read()
                            st.download_button(
                                label="📄 Download HTML",
                                data=html_bytes,
                                file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                mime="text/html",
                                use_container_width=True,
                                on_click=lambda: add_audit_event("User", "Downloaded HTML Report", "completed")
                            )
                        else:
                            st.button("📄 Download HTML", disabled=True, use_container_width=True, 
                                     help="HTML report not yet available")
                    except Exception as e:
                        st.button("📄 Download HTML", disabled=True, use_container_width=True,
                                 help=f"Error: {str(e)}")
                else:
                    st.button("📄 Download HTML", disabled=True, use_container_width=True,
                             help="Report path not available")

            # PDF Download Button
            with col2:
                pdf_path = result.get("pdf_path")
                if pdf_path:
                    try:
                        pdf_file = Path(pdf_path)
                        if pdf_file.exists() and pdf_file.suffix.lower() == ".pdf":
                            with open(pdf_file, "rb") as f:
                                pdf_bytes = f.read()
                            st.download_button(
                                label="📊 Download PDF",
                                data=pdf_bytes,
                                file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                on_click=lambda: add_audit_event("User", "Downloaded PDF Report", "completed")
                            )
                        else:
                            st.button("📊 Download PDF", disabled=True, use_container_width=True,
                                     help="PDF report not yet available")
                    except Exception as e:
                        st.button("📊 Download PDF", disabled=True, use_container_width=True,
                                 help=f"Error: {str(e)}")
                else:
                    st.button("📊 Download PDF", disabled=True, use_container_width=True,
                             help="PDF report not yet available")


# ============================================================================
# AUDIT TRAIL PANEL
# ============================================================================

def render_audit_panel() -> None:
    """Render audit trail panel (right sidebar)."""
    st.markdown("### 📜 Audit Trail")

    if not st.session_state.audit_trail:
        st.info("No events yet")
        return

    for event in st.session_state.audit_trail[:20]:  # Show last 20 events
        timestamp = event.get("timestamp", "")
        agent = event.get("agent", "Unknown")
        action = event.get("action", "")
        status = event.get("status", "")

        # Determine status color
        status_color = "🔵"
        if status.lower() in ["completed", "approved", "success"]:
            status_color = "🟢"
        elif status.lower() in ["pending", "initiated"]:
            status_color = "🟡"
        elif status.lower() in ["failed", "error"]:
            status_color = "🔴"

        st.markdown(f"""
        <div class="audit-event">
            <div class="audit-timestamp">{timestamp}</div>
            <div class="audit-agent">{status_color} {agent}</div>
            <div class="audit-action">{action}</div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================================
# ERROR AND SUCCESS DISPLAY
# ============================================================================

def render_messages() -> None:
    """Render error and success messages."""
    if st.session_state.error_message:
        st.markdown(f"""
        <div class="error-card">
            <div class="error-title">❌ Error</div>
            <div class="error-message">{st.session_state.error_message}</div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state.error_message = None

    if st.session_state.success_message:
        st.markdown(f"""
        <div class="success-card">
            <div class="success-title">✅ Success</div>
            <div class="error-message">{st.session_state.success_message}</div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state.success_message = None


# ============================================================================
# LANDING PAGE - HERO & FEATURES
# ============================================================================

def render_landing_page() -> None:
    """Render modern SaaS landing page with gradient background."""
    # Hero Section with Gradient Background
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f0f6ff 0%, #e8f1ff 50%, #f0e8ff 100%);
        padding: 80px 40px;
        text-align: center;
        border-radius: 0;
        margin: -40px -40px 40px -40px;
    ">
        <div style="max-width: 900px; margin: 0 auto;">
            <div style="font-size: 64px; margin-bottom: 20px; font-weight: 700; background: linear-gradient(135deg, #0078d4, #107c10); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                insightForge
            </div>
            <div style="font-size: 28px; font-weight: 600; color: #242424; margin-bottom: 16px;">
                AI-Powered Business Intelligence Report Generator
            </div>
            <div style="font-size: 18px; color: #595959; margin-bottom: 40px; line-height: 1.6;">
                Transform your business requirements into actionable insights.<br/>Generate prototypes, analyze data, and create executive-ready reports in minutes.
            </div>
            
            <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;">
                <div style="background: white; padding: 20px 32px; border-radius: 8px; border: 1px solid #e1e1e1; text-align: center; flex: 1; min-width: 200px; max-width: 250px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <div style="font-size: 28px; font-weight: 700; color: #0078d4; margin-bottom: 8px;">📊</div>
                    <div style="font-size: 16px; font-weight: 600; color: #242424; margin-bottom: 4px;">Smart Analysis</div>
                    <div style="font-size: 14px; color: #595959;">AI analyzes your requirements and identifies key insights</div>
                </div>
                
                <div style="background: white; padding: 20px 32px; border-radius: 8px; border: 1px solid #e1e1e1; text-align: center; flex: 1; min-width: 200px; max-width: 250px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <div style="font-size: 28px; font-weight: 700; color: #107c10; margin-bottom: 8px;">🎨</div>
                    <div style="font-size: 16px; font-weight: 600; color: #242424; margin-bottom: 4px;">Prototype Generation</div>
                    <div style="font-size: 14px; color: #595959;">Auto-generate interactive dashboard prototypes</div>
                </div>
                
                <div style="background: white; padding: 20px 32px; border-radius: 8px; border: 1px solid #e1e1e1; text-align: center; flex: 1; min-width: 200px; max-width: 250px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <div style="font-size: 28px; font-weight: 700; color: #d83b01; margin-bottom: 8px;">📋</div>
                    <div style="font-size: 16px; font-weight: 600; color: #242424; margin-bottom: 4px;">Executive Reports</div>
                    <div style="font-size: 14px; color: #595959;">Create comprehensive business intelligence reports</div>
                </div>
                
                <div style="background: white; padding: 20px 32px; border-radius: 8px; border: 1px solid #e1e1e1; text-align: center; flex: 1; min-width: 200px; max-width: 250px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <div style="font-size: 28px; font-weight: 700; color: #005a9e; margin-bottom: 8px;">🔒</div>
                    <div style="font-size: 16px; font-weight: 600; color: #242424; margin-bottom: 4px;">Enterprise Ready</div>
                    <div style="font-size: 14px; color: #595959;">Audit trails, approvals, and enterprise-grade security</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Business Requirement Card Section
    st.markdown("""
    <div style="max-width: 1000px; margin: 0 auto; padding: 0 20px;">
        <div style="
            background: linear-gradient(135deg, rgba(0, 82, 204, 0.08) 0%, rgba(0, 82, 204, 0.04) 100%);
            border: 1px solid #e1e1e1;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 40px;
        ">
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
                <div style="font-size: 32px;">📝</div>
                <div>
                    <div style="font-size: 20px; font-weight: 700; color: #242424;">Business Requirement</div>
                    <div style="font-size: 14px; color: #595959; margin-top: 4px;">Describe your business reporting need in detail. Our AI will help you create the perfect report.</div>
                </div>
            </div>
    """, unsafe_allow_html=True)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main() -> None:
    """Main application entry point."""
    # Initialize
    apply_custom_css()
    initialize_session()

    # Sidebar
    render_sidebar()

    # Main content
    render_messages()

    if st.session_state.workflow_started:
        render_header()
        render_progress()

        # Main content area
        col_main, col_audit = st.columns([3, 1])

        with col_main:
            # Render panels based on orchestrator results
            if st.session_state.orchestrator_results:
                # Requirement Panel
                if st.session_state.current_stage in ["requirements", "clarification", "prototype", "reporter", "completed"]:
                    render_requirement_panel()

                # Clarification Panel
                if st.session_state.current_stage in ["clarification", "prototype", "reporter", "completed"]:
                    render_clarification_panel()

                # Prototype Panel
                if st.session_state.current_stage in ["prototype", "reporter", "completed"]:
                    render_prototype_panel()

                # Report Panel
                if st.session_state.current_stage in ["reporter", "completed"]:
                    render_report_panel()
            else:
                st.info("Running analysis pipeline...")
        
        # Audit Trail Column
        with col_audit:
            render_audit_panel()
    else:
        # Landing Page
        render_landing_page()
        
        # Business Requirement Input Section
        #requirement = st.text_area(
         #   "Requirement:",
         #   value=st.session_state.business_requirement,
         #   height=120,
         #   placeholder="e.g., I need a dashboard to monitor sales performance across regions with KPIs for revenue, growth rate, top products, and monthly trends...",
         #   key="requirement_input",
         #   label_visibility="collapsed"
        #)
        #st.session_state.business_requirement = requirement
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("")
        
        # Action Buttons
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            pass
        with col2:
            if st.button("▶️ Start Analysis", use_container_width=True, key="start_btn_landing"):
                if not st.session_state.business_requirement.strip():
                    set_error("Please enter a requirement")
                else:
                    try:
                        st.session_state.workflow_started = True
                        st.session_state.current_stage = "requirements"
                        add_audit_event("System", "Workflow Started", "initiated")

                        # Instantiate OrchestratorAgent and run pipeline
                        from agents import orchestrator_agent
                        orchestrator = orchestrator_agent.OrchestratorAgent()
                        
                        st.session_state.orchestrator_results = orchestrator.run_pipeline(st.session_state.business_requirement)
                        
                        result = st.session_state.orchestrator_results
                        if result.get("status") == "Success":
                            st.session_state.current_stage = "completed"
                        else:
                            st.session_state.current_stage = "requirements"

                        add_audit_event("OrchestratorAgent", "Pipeline Completed", "completed")
                        set_success("Analysis completed!")
                        st.rerun()
                    except Exception as e:
                        set_error(f"Pipeline error: {str(e)}")
                        logger.exception("Pipeline execution failed")
        
        with col3:
            if st.button("🔄 Reset", use_container_width=True, key="reset_btn_landing"):
                reset_session()
                set_success("Workflow reset")
        
        st.markdown("")
        
        # Security & Privacy Info
        st.markdown("""
        <div style="
            background: #fafafa;
            border: 1px solid #e1e1e1;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            color: #595959;
            font-size: 13px;
            margin-top: 40px;
        ">
            🔒 Your data is secure and private. All processing happens in your secure environment.
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
