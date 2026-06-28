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
from agents.orchestrator_agent import OrchestratorAgent

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
# CUSTOM CSS - ENTERPRISE DARK THEME WITH GLASSMORPHISM
# ============================================================================

def apply_custom_css() -> None:
    """Apply enterprise-grade theme optimized for readability and accessibility."""
    st.markdown("""
    <style>
    /* Root Variables - High Contrast & Accessibility */
    :root {
        --primary-color: #0052cc;
        --primary-light: #0066ff;
        --primary-dark: #003d99;
        --secondary-color: #1a1a1a;
        --bg-dark: #ffffff;
        --bg-card: #f5f5f5;
        --bg-hover: #eeeeee;
        --text-primary: #1a1a1a;
        --text-secondary: #404040;
        --text-tertiary: #666666;
        --border-color: #d0d0d0;
        --success: #0b7d0b;
        --warning: #cc7700;
        --error: #b91c1c;
        --info: #0052cc;
        --line-height: 1.6;
        --letter-spacing: 0;
    }

    /* Global Styles - Clean & Clear */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        background: #ffffff;
        color: var(--text-primary);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
        font-size: 16px;
        line-height: var(--line-height);
    }

    /* Main Container */
    .main {
        background: transparent;
        padding: 0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(13, 17, 23, 0.95) 0%, rgba(22, 27, 34, 0.95) 100%);
        border-right: 1px solid var(--border-color);
        backdrop-filter: blur(10px);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }

    /* Cards and Containers */
    .stCard, [data-testid="stVerticalBlock"] > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .stCard:hover {
        background: rgba(19, 26, 45, 0.95) !important;
        border-color: var(--primary-light) !important;
        box-shadow: 0 12px 48px rgba(0, 102, 204, 0.2);
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, rgba(0, 102, 204, 0.1), rgba(0, 102, 204, 0.05));
        border-radius: 8px;
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        padding: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader:hover {
        background: linear-gradient(90deg, rgba(0, 102, 204, 0.2), rgba(0, 102, 204, 0.1));
        border-color: var(--primary-light);
    }

    .streamlit-expander {
        background: transparent;
        border: none;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 102, 204, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        cursor: pointer;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-light) 0%, #0099ff 100%);
        box-shadow: 0 6px 20px rgba(0, 102, 204, 0.4);
        transform: translateY(-2px);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Text Input */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: rgba(30, 41, 59, 0.5) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px;
        padding: 12px;
        font-size: 14px;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-light) !important;
        box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1) !important;
        background: rgba(30, 41, 59, 0.8) !important;
    }

    /* Metrics */
    .metric-card {
        background: linear-gradient(135deg, rgba(0, 102, 204, 0.1) 0%, rgba(0, 102, 204, 0.05) 100%);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        background: linear-gradient(135deg, rgba(0, 102, 204, 0.15) 0%, rgba(0, 102, 204, 0.08) 100%);
        border-color: var(--primary-light);
        box-shadow: 0 8px 24px rgba(0, 102, 204, 0.15);
    }

    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--primary-light);
        margin: 8px 0;
    }

    .metric-label {
        font-size: 12px;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }

    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 4px;
        transition: all 0.3s ease;
    }

    .badge-success {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .badge-warning {
        background: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .badge-error {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .badge-info {
        background: rgba(59, 130, 246, 0.15);
        color: #3b82f6;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }

    /* Workflow Progress */
    .workflow-stage {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        margin: 8px 0;
        transition: all 0.3s ease;
    }

    .workflow-stage.completed {
        background: rgba(16, 185, 129, 0.1);
        border-color: rgba(16, 185, 129, 0.3);
    }

    .workflow-stage.current {
        background: rgba(0, 102, 204, 0.15);
        border-color: var(--primary-light);
        box-shadow: 0 0 16px rgba(0, 102, 204, 0.2);
    }

    .workflow-stage.pending {
        background: var(--bg-card);
        border-color: var(--border-color);
        opacity: 0.6;
    }

    .stage-icon {
        font-size: 24px;
    }

    .stage-label {
        font-weight: 600;
        flex: 1;
        color: var(--text-primary);
    }

    .stage-status {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Section Divider */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 24px 0;
    }

    /* Header */
    .hero-header {
        background: linear-gradient(135deg, rgba(0, 102, 204, 0.2) 0%, rgba(0, 102, 204, 0.05) 100%);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 48px;
        text-align: center;
        backdrop-filter: blur(10px);
        margin-bottom: 32px;
    }

    .hero-title {
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary-light) 0%, #66d9ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 12px;
        letter-spacing: -1px;
    }

    .hero-subtitle {
        font-size: 24px;
        color: var(--text-secondary);
        margin-bottom: 12px;
        font-weight: 600;
    }

    .hero-description {
        font-size: 16px;
        color: var(--text-secondary);
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* Error Messages */
    .error-card {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px;
        padding: 16px;
        color: #fca5a5;
        margin: 12px 0;
    }

    .error-title {
        font-weight: 700;
        margin-bottom: 8px;
        color: #ef4444;
    }

    .error-message {
        font-size: 14px;
        line-height: 1.5;
    }

    /* Success Messages */
    .success-card {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 16px;
        color: #a7f3d0;
        margin: 12px 0;
    }

    .success-title {
        font-weight: 700;
        margin-bottom: 8px;
        color: #10b981;
    }

    /* Audit Trail */
    .audit-event {
        background: var(--bg-card);
        border-left: 4px solid var(--primary-light);
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        font-size: 13px;
        transition: all 0.3s ease;
    }

    .audit-event:hover {
        background: rgba(19, 26, 45, 0.95);
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.15);
    }

    .audit-timestamp {
        color: var(--text-secondary);
        font-size: 12px;
        font-weight: 600;
    }

    .audit-agent {
        color: var(--primary-light);
        font-weight: 700;
        margin: 4px 0;
    }

    .audit-action {
        color: var(--text-primary);
        margin: 4px 0;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .hero-header {
            padding: 24px;
        }

        .hero-title {
            font-size: 32px;
        }

        .hero-subtitle {
            font-size: 18px;
        }
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(0, 102, 204, 0.05);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(0, 102, 204, 0.3);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 102, 204, 0.5);
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
                        

                        #debug : Remove later
                        print("OrchestratorAgent =", OrchestratorAgent)
                        print("Type = ", type(OrchestratorAgent))

                        # Instantiate OrchestratorAgent and run pipeline
                        orchestrator = OrchestratorAgent()
                        #raise Exception("I AM HERE")
                        st.session_state.orchestrator_results = orchestrator.run_pipeline(st.session_state.business_requirement)
                        
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
                cols = st.columns(len(result["kpis"]))
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
    """Render prototype analysis panel."""
    if not st.session_state.orchestrator_results:
        return
    
    prototype_result = st.session_state.orchestrator_results.get("prototype_result")
    if not prototype_result:
        return

    with st.expander("🎨 **Dashboard Prototype**", expanded=True):
        result = prototype_result

        if isinstance(result, dict):
            # Bronze Layer
            if "bronze_layer" in result:
                st.markdown("#### 🥉 Bronze Layer (Source Tables)")
                bronze = result["bronze_layer"]
                if isinstance(bronze, dict):
                    st.write(f"**Tables:** {', '.join(bronze.get('tables', []))}")
                    if bronze.get('relationships'):
                        st.write(f"**Relationships:** {bronze['relationships']}")

            # Silver Layer
            if "silver_layer" in result:
                st.markdown("#### 🥈 Silver Layer (Dimensional Model)")
                silver = result["silver_layer"]
                if isinstance(silver, dict):
                    if silver.get('tables'):
                        st.write("**Dimension Tables:**")
                        for table in silver['tables']:
                            st.markdown(f"<span class='badge badge-info'>{table}</span>",
                                      unsafe_allow_html=True)
                    if silver.get('columns'):
                        st.write(f"**Key Columns:** {', '.join(silver['columns'])}")

            # Gold Layer
            if "gold_layer" in result:
                st.markdown("#### 🥇 Gold Layer (Analytics Model)")
                gold = result["gold_layer"]
                if isinstance(gold, dict):
                    if gold.get('measures'):
                        st.write("**Measures:**")
                        for measure in gold['measures']:
                            st.markdown(f"<span class='badge badge-success'>{measure}</span>",
                                      unsafe_allow_html=True)
                    if gold.get('visuals'):
                        st.write("**Visual Recommendations:**")
                        for visual in gold['visuals']:
                            st.write(f"• {visual}")

            # Approve Button
            st.markdown("---")
            if st.button("✅ Approve Prototype", use_container_width=True):
                st.session_state.current_stage = "reporter"
                add_audit_event("User", "Prototype Approved", "approved")
                set_success("Prototype approved!")
                st.rerun()


# ============================================================================
# REPORT PANEL
# ============================================================================

def render_report_panel() -> None:
    """Render report panel."""
    if not st.session_state.orchestrator_results:
        return
    
    report_result = st.session_state.orchestrator_results.get("report_result")
    if not report_result:
        return

    with st.expander("📊 **Executive Report**", expanded=True):
        result = report_result

        if isinstance(result, dict):
            # Executive Summary
            if "executive_summary" in result:
                st.markdown("#### Executive Summary")
                st.info(result["executive_summary"])

            # Business Insights
            if "business_insights" in result:
                st.markdown("#### 💡 Business Insights")
                insights = result["business_insights"]
                if isinstance(insights, list):
                    for insight in insights:
                        st.write(f"• {insight}")
                else:
                    st.write(insights)

            # Recommendations
            if "recommendations" in result:
                st.markdown("#### 🎯 Recommendations")
                recommendations = result["recommendations"]
                if isinstance(recommendations, list):
                    for idx, rec in enumerate(recommendations, 1):
                        st.write(f"{idx}. {rec}")
                else:
                    st.write(recommendations)

            # Architecture Summary
            if "architecture_summary" in result:
                st.markdown("#### 🏗️ Architecture Summary")
                st.write(result["architecture_summary"])

            # Download Section
            st.markdown("---")
            st.markdown("#### 📥 Download Report")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📄 Download HTML", use_container_width=True):
                    st.success("HTML report generated!")
                    add_audit_event("User", "Downloaded HTML Report", "completed")

            with col2:
                if st.button("📊 Download PDF", use_container_width=True):
                    st.success("PDF report generated!")
                    add_audit_event("User", "Downloaded PDF Report", "completed")


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
    render_header()

    render_messages()

    if st.session_state.workflow_started:
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
    else:
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px; color: var(--text-secondary);">
            <div style="font-size: 48px; margin-bottom: 20px;">🚀</div>
            <h3>Ready to begin?</h3>
            <p>Enter your business requirement in the sidebar and click "Start Analysis" to begin the workflow.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.columns(3)[1]:
            st.info("👈 Use the sidebar to get started")

        col_main, col_audit = st.columns([3, 1])

        with col_audit:
            st.markdown("")

    # Audit Trail Column
    with col_audit:
        render_audit_panel()


if __name__ == "__main__":
    main()
