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
    mock_data_output: dict = Field(default_factory=dict)
    prototype_output: dict = Field(default_factory=dict)
    error: str = ""


@tool
def generate_mock_data(table_name: str, columns: list, num_rows: int = 12) -> dict:
    """Generate realistic mock data for dashboard visualization"""
    mock_data = {"table_name": table_name, "columns": columns, "data": []}
    
    # Dimension categories for realistic data
    dimensions = ["Supplier A", "Supplier B", "Supplier C", "Supplier D", "Supplier E"]
    regions = ["North", "South", "East", "West", "Central"]
    categories = dimensions + regions
    
    # Generate 100-150 rows for realistic dashboard data
    num_realistic_rows = min(max(num_rows, 100), 150)
    start_date = datetime.now() - timedelta(days=num_realistic_rows - 1)
    
    for i in range(num_realistic_rows):
        row = {}
        current_date = start_date + timedelta(days=i)
        
        for col in columns:
            col_name = col.get("name", "")
            col_type = col.get("type", "string")
            
            if col_type.lower() == "date":
                row[col_name] = current_date.strftime("%Y-%m-%d")
            elif col_type.lower() == "integer":
                # Generate realistic integer counts
                row[col_name] = random.randint(50, 5000)
            elif col_type.lower() == "float":
                # Generate realistic float percentages
                row[col_name] = round(random.uniform(70, 100), 2)
            elif col_type.lower() == "currency":
                # Generate realistic currency values in 100k-500k range
                base_value = random.randint(100000, 500000)
                # Add daily variation
                variation = random.uniform(0.85, 1.15)
                row[col_name] = round(base_value * variation, 2)
            elif col_type.lower() == "string":
                # Use realistic dimension values
                row[col_name] = random.choice(categories)
            elif col_type.lower() == "percentage":
                # Generate percentage values between 70-100
                row[col_name] = round(random.uniform(70, 100), 2)
            else:
                row[col_name] = "Sample Value"
        
        mock_data["data"].append(row)
    
    return mock_data


def generate_prototype_json(requirements: dict, clarifications: dict, mock_data_output: dict) -> dict:
    """Generate comprehensive dashboard prototype JSON in Power BI Executive Dashboard style"""
    
    dashboard_title = requirements.get("dashboard_title", "Executive Analytics Dashboard")
    approved_metrics = clarifications.get("approved_metrics", [])

    while len(approved_metrics) < 4:
        approved_metrics.append({
            "name": f"Metric {len(approved_metrics) + 1}",
            "description": "Default KPI"
        }
    )
    
    # Generate mock tables and sample data
    mock_tables = []
    sample_data = []
    
    dataframes = mock_data_output.get("dataframes", {})

    for table_name, df in dataframes.items():
        mock_tables.append(
            {
            "table_name": table_name,
            "columns": list(df.columns)
        }
    )
        sample_data.append(
            {
            "table_name": table_name,
            "data": df.head(20).to_dict(orient="records")
        }
    )
    
    # Generate 4 KPI Cards for top row (from approved metrics)
    kpi_cards = []
    kpi_visual_ids = []
    for i in range(4):
        metric = approved_metrics[i] if i < len(approved_metrics) else {
            "name": f"Metric {i+1}",
            "description": "Key Performance Indicator"
        }
        kpi_id = f"visual_kpi_{i}"
        kpi_visual_ids.append(kpi_id)
        
        kpi_cards.append({
            "visual_id": kpi_id,
            "visual_type": "KPI Card",
            "title": metric.get("name", f"KPI {i+1}"),
            "data_source": f"Table_{i % max(len(mock_tables), 1)}",
            "x_axis": "Region",
            "y_axis": metric.get("name", "Value"),
            "business_justification": f"Key metric: {metric.get('description', 'Performance tracking')}. {metric.get('requirement', 'Supports business objectives.')}",
            "recommended_size": "small",
            "config": {
                "show_trend": True,
                "trend_direction": "up" if i % 2 == 0 else "stable",
                "comparison_period": "vs last month",
                "value_format": "currency" if i < 2 else "percentage",
                "color_scheme": ["#0078D4", "#107C10", "#FF8C00", "#E81B23"][i],
                "threshold_high": 80,
                "threshold_low": 20
            }
        })
    
    # Second row: Column Chart and Line Chart
    second_row_visuals = []
    
    # Column Chart
    column_chart = {
        "visual_id": "visual_column_chart",
        "visual_type": "Column Chart",
        "title": f"{approved_metrics[0].get('name', 'Performance')} by Region",
        "data_source": f"Table_0",
        "x_axis": "Region",
        "y_axis": approved_metrics[0].get("name", "Value"),
        "business_justification": "Regional performance comparison enables identification of top and underperforming areas",
        "recommended_size": "medium",
        "config": {
            "show_data_labels": True,
            "show_legend": True,
            "color_scheme": "#0078D4",
            "sort_order": "descending",
            "enable_drill_down": True,
            "drill_targets": ["Category", "Territory"]
        }
    }
    second_row_visuals.append(column_chart)
    
    # Line Chart
    line_chart = {
        "visual_id": "visual_line_chart",
        "visual_type": "Line Chart",
        "title": f"{approved_metrics[1].get('name', 'Trend')} Over Time",
        "data_source": f"Table_1",
        "x_axis": "Date",
        "y_axis": approved_metrics[1].get("name", "Value"),
        "business_justification": "Time-series trend analysis provides insights into seasonal patterns and performance momentum",
        "recommended_size": "medium",
        "config": {
            "show_data_points": True,
            "show_legend": True,
            "color_scheme": "#107C10",
            "line_style": "solid",
            "enable_drill_down": True,
            "drill_targets": ["Month", "Quarter"],
            "show_forecast": False
        }
    }
    second_row_visuals.append(line_chart)
    
    # Third row: Treemap and Pie Chart
    third_row_visuals = []
    
    # Treemap
    treemap = {
        "visual_id": "visual_treemap",
        "visual_type": "Treemap",
        "title": "Category Distribution",
        "data_source": f"Table_{2 % max(len(mock_tables), 1)}",
        "x_axis": "Category",
        "y_axis": "Performance",
        "business_justification": "Hierarchical view of category contribution and relative importance to overall performance",
        "recommended_size": "medium",
        "config": {
            "show_data_labels": True,
            "color_scheme": "gradient",
            "gradient_start": "#FFB900",
            "gradient_end": "#FF8C00",
            "enable_drill_down": True,
            "drill_targets": ["Subcategory", "Product"]
        }
    }
    third_row_visuals.append(treemap)
    
    # Pie Chart
    pie_chart = {
        "visual_id": "visual_pie_chart",
        "visual_type": "Pie Chart",
        "title": "Revenue Distribution by Supplier",
        "data_source": f"Table_{1 % max(len(mock_tables), 1)}",
        "x_axis": "Region",
        "y_axis": approved_metrics[0].get("name", "Value"),
        "business_justification": "Supplier/segment composition analysis for portfolio optimization decisions",
        "recommended_size": "medium",
        "config": {
            "show_percentage": True,
            "show_legend": True,
            "legend_position": "right",
            "color_scheme": "multi",
            "enable_drill_down": True,
            "drill_targets": ["Location", "Account"]
        }
    }
    third_row_visuals.append(pie_chart)
    
    # Fourth row: Detailed Table
    detail_table = {
        "visual_id": "visual_detail_table",
        "visual_type": "Table",
        "title": "Performance Details",
        "data_source": "Table_0",
        "x_axis": "Date",
        "y_axis": "Multiple Fields",
        "business_justification": "Comprehensive data table for detailed analysis, filtering, and exporting transaction-level insights",
        "recommended_size": "large",
        "config": {
            "show_row_numbers": True,
            "enable_sorting": True,
            "enable_filtering": True,
            "conditional_formatting": True,
            "page_size": 20,
            "columns": [
                {"name": "Date", "width": 100},
                {"name": "Region", "width": 80},
                {"name": "Category", "width": 100},
                {"name": "Performance", "width": 100},
                {"name": "Target", "width": 100}
            ]
        }
    }
    
    # Combine all visuals
    visuals = kpi_cards + second_row_visuals + third_row_visuals + [detail_table]
    
    # Comprehensive page layout grid
    pages = [
        {
            "page_id": "overview",
            "page_name": "Executive Overview",
            "visuals": [v["visual_id"] for v in visuals],
            "layout": {
                "rows": 4,
                "columns": 4,
                "grid": [
                    # Row 1: 4 KPI Cards
                    {"visual_id": "visual_kpi_0", "row": 1, "col": 1, "row_span": 1, "col_span": 1, "size": "small"},
                    {"visual_id": "visual_kpi_1", "row": 1, "col": 2, "row_span": 1, "col_span": 1, "size": "small"},
                    {"visual_id": "visual_kpi_2", "row": 1, "col": 3, "row_span": 1, "col_span": 1, "size": "small"},
                    {"visual_id": "visual_kpi_3", "row": 1, "col": 4, "row_span": 1, "col_span": 1, "size": "small"},
                    # Row 2: Column Chart and Line Chart
                    {"visual_id": "visual_column_chart", "row": 2, "col": 1, "row_span": 1, "col_span": 2, "size": "medium"},
                    {"visual_id": "visual_line_chart", "row": 2, "col": 3, "row_span": 1, "col_span": 2, "size": "medium"},
                    # Row 3: Treemap and Pie Chart
                    {"visual_id": "visual_treemap", "row": 3, "col": 1, "row_span": 1, "col_span": 2, "size": "medium"},
                    {"visual_id": "visual_pie_chart", "row": 3, "col": 3, "row_span": 1, "col_span": 2, "size": "medium"},
                    # Row 4: Detail Table
                    {"visual_id": "visual_detail_table", "row": 4, "col": 1, "row_span": 1, "col_span": 4, "size": "large"}
                ]
            }
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
            "filter_id": "region_slicer",
            "filter_type": "Dropdown",
            "display_as": "Slicer",
            "label": "Region",
            "values": ["North", "South", "East", "West", "Central"],
            "applies_to": ["all_visuals"]
        },
        {
            "filter_id": "category_slicer",
            "filter_type": "Dropdown",
            "display_as": "Slicer",
            "label": "Category",
            "values": ["Supplier A", "Supplier B", "Supplier C", "Supplier D", "Supplier E"],
            "applies_to": ["visual_column_chart", "visual_line_chart", "visual_detail_table"]
        }
    ]
    
    # Drill-down hierarchy
    drill_downs = [
        {
            "drill_id": "drill_1",
            "hierarchy_name": "Date Hierarchy",
            "levels": ["Year", "Quarter", "Month", "Day"],
            "applies_to": ["visual_line_chart", "visual_detail_table"]
        },
        {
            "drill_id": "drill_2",
            "hierarchy_name": "Geography Hierarchy",
            "levels": ["Region", "Territory", "Location"],
            "applies_to": ["visual_column_chart", "visual_pie_chart", "visual_treemap"]
        },
        {
            "drill_id": "drill_3",
            "hierarchy_name": "Category Hierarchy",
            "levels": ["Category", "Subcategory", "Product"],
            "applies_to": ["visual_treemap", "visual_detail_table"]
        }
    ]
    
    # Color rules and conditional formatting
    color_rules = [
        {
            "rule_id": "rule_1",
            "visual_id": "visual_kpi_0",
            "condition": "value > 100000",
            "color": "#00B050",
            "description": "Green for high performance"
        },
        {
            "rule_id": "rule_2",
            "visual_id": "visual_kpi_0",
            "condition": "value < 50000",
            "color": "#FF0000",
            "description": "Red for low performance"
        },
        {
            "rule_id": "rule_3",
            "visual_id": "visual_detail_table",
            "condition": "Performance > 90",
            "color": "#E2EFDA",
            "description": "Light green for exceeding targets"
        },
        {
            "rule_id": "rule_4",
            "visual_id": "visual_detail_table",
            "condition": "Performance < 70",
            "color": "#FCE4D6",
            "description": "Light red for underperformance"
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
            "page_layout": "Power BI Grid",
            "grid_size": "4x4",
            "default_theme": "Executive",
            "mobile_responsive": True,
            "recommended_canvas_size": "1920x1080"
        },
        "Client_review_notes": [
            "Power BI Executive Dashboard with 8 visuals: 4 KPI cards, 2 charts (column and line), 2 distribution visuals (treemap and pie), plus detail table",
            "Top row provides at-a-glance KPI status for executive decision making",
            "Second row enables regional and temporal trend analysis",
            "Third row shows category and supplier distribution for portfolio optimization",
            "Fourth row provides drill-down capability for detailed exploration",
            "All visuals include mock data reflecting realistic business scenarios",
            "Comprehensive filtering with date range, region, and category slicers",
            "Three-level drill-down hierarchies enable progressive disclosure of detail",
            "Conditional formatting highlights performance anomalies automatically",
            "Color scheme follows accessibility guidelines and Power BI best practices"
        ],
        "Ready_for_development": True,
        "Next_steps": [
            "Client review and approval of dashboard layout and visual selection",
            "Finalize KPI definitions and calculation formulas",
            "Validate data source connections and refresh schedules",
            "Implement drill-through actions for deeper analysis",
            "Set up scheduled alerts for KPI threshold violations",
            "Prepare for Power BI development phase with confirmed specifications"
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
        prototype = generate_prototype_json(requirements, clarifications, state.mock_data_output)
        
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


async def run_prototype_agent(structured_requirements: dict, clarification_output: dict, mock_data_output: dict) -> dict:
    """Execute the prototype agent"""
    agent = create_prototype_agent()
    
    initial_state = PrototypeState(
        structured_requirements=structured_requirements,
        clarification_output=clarification_output,
        mock_data_output=mock_data_output
    )
    
    final_state = await agent.ainvoke(initial_state)
    
    if final_state.get("error"):
        logger.error(f"Prototype agent error: {final_state.get('error')}")
        return {"error": final_state.get("error")}
    
    return final_state.get("prototype_output", {})

class PrototypeAgent:
    """Backward-compatible PrototypeAgent class"""
    
    def __init__(self):
        """Initialize the PrototypeAgent with shared LLM"""
        self.llm = get_llm()
        logger.info("PrototypeAgent initialized with LLM")
    
    async def process(self, requirement_json: dict, clarification_result: dict) -> dict:
        """
        Process requirement JSON and generate prototype.
        This method provides backward compatibility by wrapping the internal processing.
        """
        return await run_prototype_agent(requirement_json, clarification_result)
    
    def create_prototype(self, requirement_result, clarification_result, mock_data_result):
        import asyncio

        return asyncio.run(
            run_prototype_agent(requirement_result, clarification_result, mock_data_result)
        )
