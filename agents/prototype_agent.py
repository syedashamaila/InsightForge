"""
Prototype Agent - Third stage in the workflow
Generates dashboard prototypes using approved requirements and clarifications
"""

from langchain_core.messages import BaseMessage
#from langchain_openai import ChatOpenAI
from utils.llm_helper import get_llm
llm = get_llm()
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from typing import Annotated
from pydantic import BaseModel, Field
from operator import add
import json
import logging
from datetime import datetime, timedelta
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize LLM
#llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.7)


class PrototypeState(BaseModel):
    """State for the prototype agent"""
    messages: Annotated[list[BaseMessage], add] = Field(default_factory=list)
    structured_requirements: dict = Field(default_factory=dict)
    clarification_output: dict = Field(default_factory=dict)
    prototype_output: dict = Field(default_factory=dict)
    error: str = ""


@tool
def generate_mock_data(table_name: str, columns: list, num_rows: int = 12) -> dict:
    """Generate realistic mock data for dashboard visualization"""
    mock_data = {"table_name": table_name, "columns": columns, "data": []}
    
    def generate_value(col_name: str, col_type: str):
        if col_type.lower() == "date":
            start_date = datetime.now() - timedelta(days=365)
            random_days = random.randint(0, 365)
            return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")
        elif col_type.lower() == "integer":
            return random.randint(100, 100000)
        elif col_type.lower() == "float":
            return round(random.uniform(1000, 50000), 2)
        elif col_type.lower() == "string":
            categories = ["Category A", "Category B", "Category C", "Category D"]
            return random.choice(categories)
        elif col_type.lower() == "currency":
            return round(random.uniform(5000, 500000), 2)
        else:
            return "Sample Value"
    
    for i in range(num_rows):
        row = {}
        for col in columns:
            col_name = col.get("name", "")
            col_type = col.get("type", "string")
            row[col_name] = generate_value(col_name, col_type)
        mock_data["data"].append(row)
    
    return mock_data


def generate_prototype_json(requirements: dict, clarifications: dict) -> dict:
    """Generate comprehensive dashboard prototype JSON"""
    
    dashboard_title = requirements.get("dashboard_title", "Analytics Dashboard")
    approved_metrics = clarifications.get("approved_metrics", [])
    
    # Generate mock tables and sample data
    mock_tables = []
    sample_data = []
    
    for i, metric in enumerate(approved_metrics[:3]):
        columns = [
            {"name": "Date", "type": "date"},
            {"name": "Dimension", "type": "string"},
            {"name": metric.get("name", f"Metric_{i}"), "type": "currency"}
        ]
        table_data = generate_mock_data(f"Table_{i}", columns, 12)
        mock_tables.append({"table_name": table_data["table_name"], "columns": columns})
        sample_data.append(table_data)
    
    # Define visuals with business justification
    visuals = []
    for i, metric in enumerate(approved_metrics[:3]):
        visuals.append({
            "visual_id": f"visual_{i}",
            "visual_type": ["Column Chart", "Line Chart", "KPI Card"][i % 3],
            "title": f"{metric.get('name', f'Metric {i}')} Trend",
            "data_source": f"Table_{i % len(mock_tables)}",
            "x_axis": "Date",
            "y_axis": metric.get("name", "Value"),
            "business_justification": f"This visual tracks {metric.get('description', 'performance')} over time, directly addressing the requirement: {metric.get('requirement', 'N/A')}",
            "recommended_size": "medium"
        })
    
    # Page layout
    pages = [
        {
            "page_id": "overview",
            "page_name": "Overview",
            "visuals": [v["visual_id"] for v in visuals[:3]],
            "layout": {
                "rows": 2,
                "columns": 2,
                "grid": [
                    {"visual_id": visuals[0]["visual_id"] if len(visuals) > 0 else None, "row": 1, "col": 1, "size": "medium"},
                    {"visual_id": visuals[1]["visual_id"] if len(visuals) > 1 else None, "row": 1, "col": 2, "size": "medium"},
                    {"visual_id": visuals[2]["visual_id"] if len(visuals) > 2 else None, "row": 2, "col": 1, "size": "medium"}
                ]
            }
        }
    ]
    
    # KPI Cards
    kpi_cards = [
        {
            "kpi_id": "kpi_1",
            "title": "Total Revenue",
            "value_field": approved_metrics[0]["name"] if approved_metrics else "Value",
            "comparison": "vs last month",
            "trend": "up"
        },
        {
            "kpi_id": "kpi_2",
            "title": "Average Performance",
            "value_field": approved_metrics[1]["name"] if len(approved_metrics) > 1 else "Value",
            "comparison": "vs average",
            "trend": "stable"
        }
    ]
    
    # Filters and Slicers
    filters_slicers = [
        {
            "filter_id": "date_filter",
            "filter_type": "DateRange",
            "display_as": "Slicer",
            "label": "Date Range",
            "default_range": "Last 12 Months",
            "applies_to": ["all_visuals"]
        },
        {
            "filter_id": "dimension_slicer",
            "filter_type": "Dropdown",
            "display_as": "Slicer",
            "label": "Category",
            "values": ["Category A", "Category B", "Category C", "Category D"],
            "applies_to": ["visual_0", "visual_1"]
        }
    ]
    
    # Drill-down hierarchy
    drill_downs = [
        {
            "drill_id": "drill_1",
            "hierarchy_name": "Date Hierarchy",
            "levels": ["Year", "Quarter", "Month", "Day"],
            "applies_to": ["visual_0"]
        },
        {
            "drill_id": "drill_2",
            "hierarchy_name": "Category Hierarchy",
            "levels": ["Region", "Territory", "Store"],
            "applies_to": ["visual_1"]
        }
    ]
    
    # Color rules and conditional formatting
    color_rules = [
        {
            "rule_id": "rule_1",
            "visual_id": "kpi_1",
            "condition": "value > 100000",
            "color": "#00B050",
            "description": "Green for high performance"
        },
        {
            "rule_id": "rule_2",
            "visual_id": "kpi_1",
            "condition": "value < 50000",
            "color": "#FF0000",
            "description": "Red for low performance"
        },
        {
            "rule_id": "rule_3",
            "visual_id": "kpi_1",
            "condition": "value between 50000 and 100000",
            "color": "#FFC000",
            "description": "Yellow for moderate performance"
        }
    ]
    
    prototype_json = {
        "dashboard_title": dashboard_title,
        "version": "1.0",
        "created_date": datetime.now().isoformat(),
        "Pages": pages,
        "Visuals": visuals,
        "Mock_tables": mock_tables,
        "Sample_data": sample_data,
        "KPI_cards": kpi_cards,
        "Filters": filters_slicers,
        "Slicers": [f for f in filters_slicers if f["display_as"] == "Slicer"],
        "Drill_downs": drill_downs,
        "color_rules": color_rules,
        "Layout": {
            "page_layout": "Grid",
            "grid_size": "2x2",
            "default_theme": "Modern",
            "mobile_responsive": True,
            "recommended_canvas_size": "1920x1080"
        },
        "Client_review_notes": [
            "This prototype demonstrates the key metrics and dimensions approved in the clarification phase",
            "All visuals include mock data to simulate real-world performance",
            "Recommended to validate visual types and layout with stakeholders before development",
            "Color scheme follows accessibility guidelines for colorblind users",
            "Drill-down hierarchies enable deeper exploration of data",
            "Date range filter applies globally for easy period comparison"
        ],
        "Ready_for_development": True,
        "Next_steps": [
            "Client review and feedback on visual recommendations",
            "Finalize color scheme and branding",
            "Validate drill-down hierarchies",
            "Prepare for Power BI development phase"
        ]
    }
    
    return prototype_json


async def prototype_node(state: PrototypeState) -> PrototypeState:
    """Main prototype generation node"""
    try:
        logger.info("Starting prototype generation")
        
        requirements = state.structured_requirements
        clarifications = state.clarification_output
        
        # Generate prototype JSON
        prototype = generate_prototype_json(requirements, clarifications)
        
        state.prototype_output = prototype
        logger.info("Prototype generation completed successfully")
        
    except Exception as e:
        logger.error(f"Error in prototype generation: {str(e)}")
        state.error = str(e)
    
    return state


def create_prototype_agent():
    """Create and return the prototype agent workflow"""
    workflow = StateGraph(PrototypeState)
    
    # Add nodes
    workflow.add_node("prototype", prototype_node)
    
    # Add edges
    workflow.add_edge(START, "prototype")
    workflow.add_edge("prototype", END)
    
    return workflow.compile()


async def run_prototype_agent(structured_requirements: dict, clarification_output: dict) -> dict:
    """Execute the prototype agent"""
    agent = create_prototype_agent()
    
    initial_state = PrototypeState(
        structured_requirements=structured_requirements,
        clarification_output=clarification_output
    )
    
    final_state = await agent.ainvoke(initial_state)
    
    if final_state.error:
        logger.error(f"Prototype agent error: {final_state.error}")
        return {"error": final_state.error}
    
    return final_state.prototype_output


class PrototypeAgent:
    """Backward-compatible PrototypeAgent class"""
    
    def __init__(self):
        """Initialize the PrototypeAgent with shared LLM"""
        self.llm = get_llm()
        logger.info("PrototypeAgent initialized with LLM")
    
    async def process(self, requirement_json: dict) -> dict:
        """
        Process requirement JSON and generate prototype.
        This method provides backward compatibility by wrapping the internal processing.
        """
        return await run_prototype_agent(requirement_json, {})
