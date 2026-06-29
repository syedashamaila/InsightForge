import os
import sys

print("CWD:", os.getcwd())
print("Python Path:", sys.path)
print("FILE:", __file__)


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
#import agents
#from agents.clarification_agent import ClarificationAgent


# Page config
st.set_page_config(
    page_title="insightForge",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# CUSTOM CSS for modern SaaS styling
# ============================================================================
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        height: 100%;
        width: 100%;
    }
    
    /* Main container */
            
    [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #eef6ff 0%, #ffffff 45%, #f3edff 100%);
    }
    .main .block-container {
       max-width: 1400px;
       padding-top: 1rem;
       padding-bottom: 1rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e8e8e8;
    }
    
    /* Logo section */
    .logo-section {
        padding: 28px 20px;
        text-align: center;
        border-bottom: 1px solid #ececec;
        margin-bottom: 24px;
    }
    
    .logo-section img{
            width: 64px;
            margin-bottom:12px;
    }
            
    .logo-icon {
        font-size: 48px;
        margin-bottom: 10px;
    }
    
    .logo-text {
        font-size: 30px;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #3366ff 0%, #7366ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Card styling */
    .card {
        background: #ffffff;
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
        border: 1px solid #edf1f7;
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }
    
    .card:hover {
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.15);
        transform: translateY(-4px);
    }
    
    .card-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 8px;
        color: #1f2937;
    }
            
    .section-title{
            font-size:28px;
            font-weight:700;
            color:#1e293b;
            margin-bottom:20px;
            }
    .center{
            text-align:center;
            }

    .card-subtitle {
        font-size: 14px;
        color: #666;
        margin-bottom: 16px;
        line-height: 1.5;
    }
    
    /* Workflow cards */
    .workflow-card {
        background: #ffffff;
        border-radius: 18px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
        border: 1px solid #edf1f7;
        transition: all 0.3s ease;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .workflow-card:hover {
        box-shadow: 0 20px 45px rgba(15, 23, 42, 0.15);
        transform: translateY(-6px);
    }
    
    .workflow-icon {
        font-size: 42px;
        margin-bottom: 18px;
    }
    
    .workflow-title {
        font-size: 20px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 12px;
    }
    
    .workflow-status {
            display: inline-block;
        font-size: 13px;
        font-weight: 600;
        color: #16a34a;
        padding: 8px 18px;
        background: #ecfdf5;
        border-radius: 999px;
        margin-top: 18px;
    }
    
    /* Hero section */
    .hero {
        text-align: center;
        padding: 60px 20px;
        margin-bottom: 40px;
    }
    
    .hero-logo {
        font-size: 72px;
        margin-bottom: 20px;
    }
    
    .hero-title {
        font-size: 56px;
        font-weight: 700;
        margin-bottom: 12px;
        background: linear-gradient(135deg, #1a1a1a 0%, #3366ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .hero-subtitle {
        font-size: 20px;
        color: #666;
        margin-bottom: 16px;
        font-weight: 600;
    }
    
    .hero-description {
        font-size: 16px;
        color: #888;
        max-width: 600px;
        margin: 0 auto 40px;
        line-height: 1.6;
    }
            
    
    
    /* Status card */
    .status-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin-top: 20px;
        border: 1px solid #e0e0e0;
    }
    
    .status-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        font-size: 14px;
    }
    
    .status-label {
        color: #666;
    }
    
    .status-value {
        font-weight: 600;
        color: #1a1a1a;
    }
    
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
    }
    
    .status-indicator.active {
        background: #10b981;
    }
    
    /* Timeline */
    .timeline {
        position: relative;
        padding: 20px 0;
    }
    
    .timeline-item {
        display: flex;
        margin-bottom: 24px;
        position: relative;
        padding-left: 40px;
    }
    
    .timeline-dot {
        position: absolute;
        left: 0;
        width: 12px;
        height: 12px;
        background: #3366ff;
        border-radius: 50%;
        top: 5px;
        border: 3px solid white;
        box-shadow: 0 0 0 2px #3366ff;
    }
    
    .timeline-content {
        background: white;
        border-radius: 8px;
        padding: 12px 16px;
        flex: 1;
        border-left: 2px solid #e0e0e0;
        padding-left: 16px;
    }
    
    .timeline-time {
        font-size: 12px;
        color: #999;
        margin-bottom: 4px;
    }
    
    .timeline-message {
        font-size: 14px;
        color: #333;
        font-weight: 500;
    }
    
    /* KPI cards */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #3366ff;
    }
    
    .kpi-value {
        font-size: 32px;
        font-weight: 700;
        color: #1a1a1a;
        margin: 10px 0;
    }
    
    .kpi-label {
        font-size: 12px;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-change {
        font-size: 12px;
        color: #10b981;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session() -> None:
    """Initialize Streamlit session state with default values."""
    defaults = {
        "page": "Home",
        "business_requirement": "",
        "workflow_started": False,
        "current_stage": "idle",
        "orchestrator_results": None,
        "audit_trail": [],
        "error_message": None,
        "success_message": None,
        "analysis_complete": False,
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
    st.session_state.page = "Home"
    st.session_state.analysis_complete = False
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

initialize_session()


# ============================================================================
# SIDEBAR AND NAVIGATION
# ============================================================================

# Sidebar
with st.sidebar:
    # Logo section
    st.markdown("""
    <div class="logo-section">
        <div class="logo-icon">⚡</div>
        <div class="logo-text">insightForge</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    st.markdown("---")
    
    if st.button("🏠 Home", use_container_width=True, key="nav_home"):
        st.session_state.page = "Home"
    
    if st.button("📊 Dashboard", use_container_width=True, key="nav_dashboard"):
        st.session_state.page = "Dashboard"
    
    if st.button("🎨 Prototype", use_container_width=True, key="nav_prototype"):
        st.session_state.page = "Prototype"
    
    if st.button("📄 Reports", use_container_width=True, key="nav_reports"):
        st.session_state.page = "Reports"
    
    if st.button("🔍 Audit Trail", use_container_width=True, key="nav_audit"):
        st.session_state.page = "Audit Trail"
    
    if st.button("⚙️ Settings", use_container_width=True, key="nav_settings"):
        st.session_state.page = "Settings"
    
    # Divider
    st.markdown("---")
    
    # Theme selector
    st.markdown("**Theme**")
    theme = st.selectbox("Select theme", ["Light", "Dark"], key="theme_selector")
    
    # System Status
    st.markdown("**System Status**")
    st.markdown("""
    <div class="status-card">
        <div class="status-item">
            <span class="status-label">API Status</span>
            <span class="status-value"><span class="status-indicator active"></span> Operational</span>
        </div>
        <div class="status-item">
            <span class="status-label">Workflow</span>
            <span class="status-value"><span class="status-indicator active"></span> Running</span>
        </div>
        <div class="status-item">
            <span class="status-label">Database</span>
            <span class="status-value"><span class="status-indicator active"></span> Connected</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


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


# Main content
render_messages()

if st.session_state.page == "Home":
    # Hero section
    st.markdown("""
    <div class="hero">
        <div class="hero-logo">⚡</div>
        <div class="hero-title">insightForge</div>
        <div class="hero-subtitle">AI-Powered Business Intelligence Report Generator</div>
        <div class="hero-description">
            Transform your business requirements into actionable insights.<br>
            Generate prototypes, analyze data, and create executive-ready reports in minutes.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Business Requirement Card
    #st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<div class="card-title">📋 Business Requirement</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-subtitle">Describe your business reporting need in detail. Our AI will help you create the perfect report.</div>', unsafe_allow_html=True)
    
    with col2:
        with st.expander("📚 Examples"):
            st.markdown("""
            - Dashboard to monitor sales performance across regions with KPIs
            - Customer segmentation report with purchase behavior analysis
            - Supply chain efficiency dashboard with inventory metrics
            - Marketing campaign ROI analysis and performance tracking
            """)
    
    # Text area
    business_req = st.text_area(
        label="Enter your business requirement",
        value=st.session_state.business_requirement,
        height=120,
        placeholder="e.g., I need a dashboard to monitor sales performance across regions with KPIs for revenue, growth rate, top products, and monthly trends...",
        key="requirement_input"
    )
    st.session_state.business_requirement = business_req
    
    # Start Analysis button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🚀 Start Analysis", use_container_width=True, key="start_analysis"):
            st.write("1. Button clicked")
            
            if not st.session_state.business_requirement.strip():
                set_error("Please enter a requirement")
            else:
                st.write("2. Validation passed")
                try:
                    st.write("3. Entered Try Block")
                    st.session_state.workflow_started = True
                    st.session_state.current_stage = "requirements"
                    add_audit_event("System", "Workflow Started", "initiated")

                    st.write("4. About to import orchestrator_agent")
                    # Instantiate OrchestratorAgent and run pipeline
                    from agents.orchestrator_agent import OrchestratorAgent
                    orchestrator = OrchestratorAgent()
                    st.session_state.orchestrator_results = orchestrator.run_pipeline(st.session_state.business_requirement)
                    st.write("5. Pipeline executed")

                    result = st.session_state.orchestrator_results
                    if result.get("status") == "Success":
                        st.session_state.current_stage = "Completed"
                    else:
                        st.session_state.current_stage = "requirements"
                        #set_error("Pipeline failed. Please check the logs for details.")

                    add_audit_event("OrchestratorAgent", "Pipeline Completed", "completed")
                    set_success("Analysis completed!")

                    st.write("✅ Analysis completed! Click the Dashboard tab from the left navigation panel to view the results.")

                    st.session_state.analysis_complete = True
                    st.session_state.page = "Dashboard"
                    st.rerun()
                except Exception as e:
                    set_error(f"Pipeline error: {str(e)}")
                    logger.exception("Pipeline execution failed")

    
    # Workflow Cards
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; margin-bottom: 30px;'>Workflow Overview</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        st.markdown("""
        <div class="workflow-card">
            <div class="workflow-icon">🔍</div>
            <div class="workflow-title">Smart Analysis</div>
            <div class="card-subtitle" style="margin: 8px 0; font-size: 13px;">AI analyzes your requirements and identifies key insights</div>
            <div class="workflow-status">Ready</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="workflow-card">
            <div class="workflow-icon">🎨</div>
            <div class="workflow-title">Prototype Generation</div>
            <div class="card-subtitle" style="margin: 8px 0; font-size: 13px;">Auto-generate interactive dashboard prototypes</div>
            <div class="workflow-status">Ready</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="workflow-card">
            <div class="workflow-icon">📊</div>
            <div class="workflow-title">Executive Reports</div>
            <div class="card-subtitle" style="margin: 8px 0; font-size: 13px;">Create comprehensive business intelligence reports</div>
            <div class="workflow-status">Ready</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="workflow-card">
            <div class="workflow-icon">🛡️</div>
            <div class="workflow-title">Enterprise Ready</div>
            <div class="card-subtitle" style="margin: 8px 0; font-size: 13px;">Audit trails, approvals, and enterprise-grade security</div>
            <div class="workflow-status">Ready</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Security note
    st.markdown("""
    <div style='text-align: center; margin-top: 40px; padding: 20px; background: #f0f4ff; border-radius: 8px; color: #666; font-size: 14px;'>
        🔒 Your data is secure and private. All processing happens in your secure environment.
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "Dashboard":
    st.markdown("## 📊 Dashboard")

    render_progress()
    
    # Mock data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    regions = (['North', 'South', 'East', 'West'] * (len(dates) // 4 + 1))[:len(dates)]
    mock_data = pd.DataFrame({
        'Date': dates,
        'Revenue': [50000 + i*100 + (i%7)*5000 for i in range(len(dates))],
        'Orders': [100 + i + (i%7)*20 for i in range(len(dates))],
        'Region': regions
    })
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4, gap="small")
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Revenue</div>
            <div class="kpi-value">${mock_data['Revenue'].sum():,.0f}</div>
            <div class="kpi-change">↑ 12.5% vs last period</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Orders</div>
            <div class="kpi-value">{mock_data['Orders'].sum():,.0f}</div>
            <div class="kpi-change">↑ 8.2% vs last period</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Avg Order Value</div>
            <div class="kpi-value">${mock_data['Revenue'].sum() / mock_data['Orders'].sum():.0f}</div>
            <div class="kpi-change">↑ 4.1% vs last period</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Growth Rate</div>
            <div class="kpi-value">23.4%</div>
            <div class="kpi-change">↑ 5.3% vs last period</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        date_range = st.date_input("Date Range", value=(mock_data['Date'].min(), mock_data['Date'].max()))
    with col2:
        regions = st.multiselect("Regions", ['North', 'South', 'East', 'West'], default=['North', 'South', 'East', 'West'])
    with col3:
        metric = st.selectbox("Metric", ['Revenue', 'Orders'])
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        # Line chart
        fig_line = px.line(mock_data, x='Date', y='Revenue', title='Revenue Trend', markers=True)
        fig_line.update_layout(height=400, template='plotly_white', hovermode='x unified')
        st.plotly_chart(fig_line, use_container_width=True)
    
    with col2:
        # Bar chart
        region_data = pd.DataFrame({
            'Region': ['North', 'South', 'East', 'West'],
            'Revenue': [1500000, 1200000, 1800000, 1100000]
        })
        fig_bar = px.bar(region_data, x='Region', y='Revenue', title='Revenue by Region', color='Region')
        fig_bar.update_layout(height=400, template='plotly_white', showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        # Pie chart
        fig_pie = px.pie(region_data, values='Revenue', names='Region', title='Market Share by Region')
        fig_pie.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Treemap
        treemap_data = pd.DataFrame({
            'Category': ['North', 'South', 'East', 'West'],
            'Value': [1500000, 1200000, 1800000, 1100000],
            'Parent': ['Total', 'Total', 'Total', 'Total']
        })
        fig_tree = px.treemap(treemap_data, labels='Category', parents='Parent', values='Value', title='Revenue Distribution')
        fig_tree.update_layout(height=400)
        st.plotly_chart(fig_tree, use_container_width=True)
    
    st.markdown("---")
    
    # Data table
    st.markdown("### Data Table")
    st.dataframe(mock_data.head(20), use_container_width=True)

elif st.session_state.page == "Prototype":
    st.markdown("## 🎨 Dashboard Prototype")
    
    st.markdown("""
    <div class="card">
        <div class="card-title">Generated Dashboard Prototype</div>
        <div class="card-subtitle">This is your auto-generated interactive dashboard based on your requirements.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Mock prototype visualization
    dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
    prototype_data = pd.DataFrame({
        'Date': dates,
        'Metric1': [100 + i*0.5 + (i%7)*10 for i in range(len(dates))],
        'Metric2': [80 + i*0.3 + (i%5)*15 for i in range(len(dates))]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.area(prototype_data, x='Date', y='Metric1', title='Prototype Metric 1')
        fig.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(prototype_data, x='Date', y='Metric2', title='Prototype Metric 2', markers=True)
        fig.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### Download Prototype")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            label="📥 Download as JSON",
            data=json.dumps({"prototype": "data"}, indent=2),
            file_name="prototype.json",
            mime="application/json"
        )
    
    with col2:
        st.download_button(
            label="📥 Download as CSV",
            data=prototype_data.to_csv(index=False),
            file_name="prototype_data.csv",
            mime="text/csv"
        )

elif st.session_state.page == "Reports":
    st.markdown("## 📄 Reports")
    
    st.markdown("""
    <div class="card">
        <div class="card-title">Generated Reports</div>
        <div class="card-subtitle">Your executive-ready reports are ready for download and sharing.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Report items
    reports = [
        {"title": "Executive Summary Report", "date": "2024-12-19", "size": "2.4 MB"},
        {"title": "Detailed Analysis Report", "date": "2024-12-19", "size": "5.1 MB"},
        {"title": "Data Insights Report", "date": "2024-12-19", "size": "1.8 MB"},
    ]
    
    for report in reports:
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{report['title']}**")
            st.markdown(f"*Generated: {report['date']}*")
        
        with col2:
            st.markdown(f"{report['size']}")
        
        with col3:
            st.download_button("📥 PDF", data="", file_name=f"{report['title']}.pdf", key=f"pdf_{report['title']}")
        
        with col4:
            st.download_button("📥 Excel", data="", file_name=f"{report['title']}.xlsx", key=f"xlsx_{report['title']}")
        
        st.markdown("---")

elif st.session_state.page == "Audit Trail":
    st.markdown("## 🔍 Audit Trail")
    
    st.markdown("""
    <div class="card">
        <div class="card-title">Event Timeline</div>
        <div class="card-subtitle">Complete history of all actions and events in your analysis workflow.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Mock audit events
    now = datetime.now()
    events = [
        {"time": now - timedelta(minutes=5), "action": "Analysis Started", "user": "Admin User", "status": "Success"},
        {"time": now - timedelta(minutes=10), "action": "Business Requirement Submitted", "user": "Admin User", "status": "Success"},
        {"time": now - timedelta(minutes=15), "action": "Dashboard Prototype Generated", "user": "System", "status": "Success"},
        {"time": now - timedelta(minutes=20), "action": "Report Generated", "user": "System", "status": "Success"},
        {"time": now - timedelta(minutes=25), "action": "Report Approved", "user": "Manager", "status": "Success"},
    ]
    
    st.markdown("""
    <div class="timeline">
    """, unsafe_allow_html=True)
    
    for event in events:
        st.markdown(f"""
        <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
                <div class="timeline-time">{event['time'].strftime('%Y-%m-%d %H:%M:%S')}</div>
                <div class="timeline-message"><strong>{event['action']}</strong> by {event['user']}</div>
                <div style="font-size: 12px; color: #10b981; margin-top: 4px;">✓ {event['status']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "Settings":
    st.markdown("## ⚙️ Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">Display Settings</div>
        </div>
        """, unsafe_allow_html=True)
        
        theme = st.radio("Theme", ["Light", "Dark"], key="settings_theme")
        language = st.selectbox("Language", ["English", "Spanish", "French", "German"])
        
        st.markdown("""
        <div class="card">
            <div class="card-title">Notifications</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.checkbox("Email Notifications", value=True)
        st.checkbox("Report Alerts", value=True)
        st.checkbox("System Updates", value=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">System Information</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="status-card">
            <div class="status-item">
                <span class="status-label">Application Version</span>
                <span class="status-value">1.0.0</span>
            </div>
            <div class="status-item">
                <span class="status-label">API Status</span>
                <span class="status-value"><span class="status-indicator active"></span> Operational</span>
            </div>
            <div class="status-item">
                <span class="status-label">Workflow Status</span>
                <span class="status-value"><span class="status-indicator active"></span> Running</span>
            </div>
            <div class="status-item">
                <span class="status-label">Database</span>
                <span class="status-value"><span class="status-indicator active"></span> Connected</span>
            </div>
            <div class="status-item">
                <span class="status-label">Last Updated</span>
                <span class="status-value">{datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <div class="card-title">About insightForge</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        insightForge is an AI-powered business intelligence platform designed to transform business requirements into actionable insights.
        
        © 2024 insightForge. All rights reserved.
        """)
