from __future__ import annotations

import logging
from typing import Dict, List, Any, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from langgraph.graph import StateGraph, START, END

from langchain_core.messages import BaseMessage

from pydantic import BaseModel, Field

from typing import Annotated
from operator import add


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class ReporterState(BaseModel):
    """
    State used by LangGraph.
    """

    messages: Annotated[list[BaseMessage], add] = Field(default_factory=list)

    prototype_output: dict = Field(default_factory=dict)

    mock_data_output: dict = Field(default_factory=dict)

    dashboard_output: dict = Field(default_factory=dict)

    error: str = ""

class ReporterEngine:
    """
    Reads Prototype JSON

    +
    Mock Data

    and generates Plotly Figures.
    """

    def __init__(self):

        logger.info("Reporter Engine Initialized")

        self.prototype = {}

        self.dataframes = {}

        self.figures = []




# Main Initialization

    def load_inputs(
            self,
            prototype_output: dict,
            mock_data_output: dict,
        ):

            self.prototype = prototype_output

            self.dataframes = mock_data_output.get(
                "dataframes",
                {}
            )




    #Helper 1 : Returns dataframe

    def get_dataframe(
            self,
            table_name: str
        ) -> Optional[pd.DataFrame]:

            return self.dataframes.get(table_name)



    #Helper 2 : Find first numeric column

    def first_numeric_column(
            self,
            df: pd.DataFrame
        ):

            cols = df.select_dtypes(
                include="number"
            ).columns.tolist()

            if cols:

                return cols[0]

            return None




    # Helper 3 : Find first categorical column

    def first_dimension_column(
            self,
            df: pd.DataFrame
        ):

            object_cols = df.select_dtypes(
                include=["object"]
            ).columns.tolist()

            if object_cols:

                return object_cols[0]

            return None


    # Helper 4 :Validate requested column

    def safe_column(
            self,
            df: pd.DataFrame,
            column_name: str,
            fallback=None
        ):

            if column_name in df.columns:

                return column_name

            return fallback


    # Helper 5 : Aggregate data automatically

    def aggregate_data(

        self,

        df,

        x_axis,

        y_axis

    ):

        x_axis = self.safe_column(

            df,

            x_axis,

            self.first_dimension_column(df)

        )

        y_axis = self.safe_column(

            df,

            y_axis,

            self.first_numeric_column(df)

        )

        if x_axis is None:

            return None

        if y_axis is None:

            return None

        grouped = (

            df

            .groupby(x_axis)

            [y_axis]

            .sum()

            .reset_index()

        )

        return grouped




    # Helper 6 : Creates empty figure

    def empty_chart(
            self,
            title: str
        ):

            fig = go.Figure()

            fig.add_annotation(

                text="No Data",

                x=0.5,

                y=0.5,

                showarrow=False,

                font=dict(size=22)

            )

            fig.update_layout(

                title=title

            )

            return fig


    # Helper 7 : Register figure

    def add_figure(
            self,
            visual_id,
            figure,
            visual=None
        ):

            self.figures.append(

                {

                    "visual_id": visual_id,
                    "title": visual.get("title", "Visualization") if visual else "Visualization",
                    "type": visual.get("type", "Chart") if visual else "Chart",
                    "figure": figure,
                    "value": visual.get("value") if visual else None,
                    "data": visual.get("data") if visual else None,

                }

            )

    # 1. Build KPI Card

    def build_kpi_card(self, visual: dict):

        table_name = visual.get("data_source")

        df = self.get_dataframe(table_name)

        if df is None:
            return self.empty_chart(visual["title"])

        y_axis = visual.get("y_axis")

        y_axis = self.safe_column(
            df,
            y_axis,
            self.first_numeric_column(df)
        )

        if y_axis is None:
            return self.empty_chart(visual["title"])

        value = float(df[y_axis].sum())

        fig = go.Figure(
            go.Indicator(
                mode="number",
                value=value,
                title={
                    "text": visual["title"]
                }
            )
        )

        fig.update_layout(
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            ),
            height=220
        )

        return fig


    # 2. Build Column Chart

    def build_column_chart(self, visual: dict):

        table_name = visual.get("data_source")

        df = self.get_dataframe(table_name)

        if df is None:
            return self.empty_chart(
                visual["title"]
            )

        grouped = self.aggregate_data(

            df,

            visual.get("x_axis"),

            visual.get("y_axis")

        )

        if grouped is None:
            return self.empty_chart(
                visual["title"]
            )

        fig = px.bar(

            grouped,

            x=grouped.columns[0],

            y=grouped.columns[1],

            title=visual["title"]

        )

        fig.update_layout(

            template="plotly_white",

            height=450

        )

        return fig


    # 3. Build Line Chart

    def build_line_chart(self, visual: dict):

        table_name = visual.get("data_source")

        df = self.get_dataframe(table_name)

        if df is None:

            return self.empty_chart(
                visual["title"]
            )

        grouped = self.aggregate_data(

            df,

            visual.get("x_axis"),

            visual.get("y_axis")

        )

        if grouped is None:

            return self.empty_chart(
                visual["title"]
            )

        fig = px.line(

            grouped,

            x=grouped.columns[0],

            y=grouped.columns[1],

            markers=True,

            title=visual["title"]

        )

        fig.update_layout(

            template="plotly_white",

            height=450

        )

        return fig


    # 4. Visual Dispatcher

    # Now add this function.

    # This automatically chooses which Plotly chart to build.

    def build_visual(self, visual: dict):

        visual_type = visual.get(

            "visual_type",

            ""

        ).lower()

        if visual_type == "kpi card":

            return self.build_kpi_card(visual)

        elif visual_type == "column chart":

            return self.build_column_chart(visual)

        elif visual_type == "line chart":

            return self.build_line_chart(visual)

        elif visual_type == "pie chart":

            return self.build_pie_chart(visual)

        elif visual_type == "treemap":

            return self.build_treemap(visual)

        elif visual_type == "table":

            return self.build_table(visual)

        return self.empty_chart(

            visual.get(

                "title",

                "Unsupported Visual"

            )

        )


    # 1. Pie Chart

    def build_pie_chart(self, visual: dict):

        table_name = visual.get("data_source")

        df = self.get_dataframe(table_name)

        if df is None:
            return self.empty_chart(visual["title"])

        grouped = self.aggregate_data(
            df,
            visual.get("x_axis"),
            visual.get("y_axis")
        )

        if grouped is None:
            return self.empty_chart(visual["title"])

        fig = px.pie(

            grouped,

            names=grouped.columns[0],

            values=grouped.columns[1],

            title=visual["title"]

        )

        fig.update_layout(

            template="plotly_white",

            height=450

        )

        return fig


    # 2. Treemap

    def build_treemap(self, visual: dict):

        table_name = visual.get("data_source")

        df = self.get_dataframe(table_name)

        if df is None:
            return self.empty_chart(visual["title"])

        grouped = self.aggregate_data(

            df,

            visual.get("x_axis"),

            visual.get("y_axis")

        )

        if grouped is None:
            return self.empty_chart(visual["title"])

        fig = px.treemap(

            grouped,

            path=[grouped.columns[0]],

            values=grouped.columns[1],

            title=visual["title"]

        )

        fig.update_layout(

            template="plotly_white",

            height=450

        )

        return fig


    # 3. Table

    def build_table(self, visual: dict):

        table_name = visual.get("data_source")

        df = self.get_dataframe(table_name)

        if df is None:
            return self.empty_chart(visual["title"])

        page_size = (
            visual
            .get("config", {})
            .get("page_size", 20)
        )

        df = df.head(page_size)

        fig = go.Figure(

            data=[

                go.Table(

                    header=dict(

                        values=list(df.columns),

                        fill_color="#4472C4",

                        font=dict(color="white", size=12),

                        align="left"

                    ),

                    cells=dict(

                        values=[df[col] for col in df.columns],

                        align="left"

                    )

                )

            ]

        )

        fig.update_layout(

            title=visual["title"],

            height=500

        )

        return fig

    # 1. Render Dashboard

    def render_dashboard(self):

        """
        Reads Prototype JSON and generates
        Plotly figures for every visual.
        """

        self.figures = []

        visuals = self.prototype.get("Visuals", [])

        logger.info(
            f"Rendering {len(visuals)} visuals..."
        )

        for visual in visuals:

            try:

                fig = self.build_visual(
                    visual
                )

                self.add_figure(

                    visual["visual_id"],

                    fig,
                    visual

                )

                logger.info(
                    f"Built {visual['visual_type']}"
                )

            except Exception as ex:

                logger.exception(ex)

                self.add_figure(

                    visual["visual_id"],

                    self.empty_chart(
                        visual.get(
                            "title",
                            "Error"
                        ),
                    visual
                    )

                )

        return {

            "dashboard_title":
                self.prototype.get(
                    "dashboard_title",
                    "Dashboard"
                ),

            "pages":
                self.prototype.get(
                    "Pages",
                    []
                ),

            "layout":
                self.prototype.get(
                    "Layout",
                    {}
                ),

            "figures":
                self.figures

        }


    # 2. Convenience Function

    def generate_dashboard(

        self,

        prototype_output,

        mock_data_output

    ):

        self.load_inputs(

            prototype_output,

            mock_data_output

        )

        return self.render_dashboard()



    def get_dashboard_summary(self):

        return {

            "title":

                self.prototype.get(

                    "dashboard_title"

                ),

            "visual_count":

                len(

                    self.prototype.get(

                        "Visuals",

                        []

                    )

                ),

            "tables":

                list(

                    self.dataframes.keys()

                )

        }

    # 1. reporter_node()

    async def reporter_node(self, state: ReporterState) -> ReporterState:
        """
        LangGraph node for Reporter Agent.
        Generates Plotly dashboard figures from the Prototype JSON.
        """

        try:

            logger.info("Starting Reporter Agent...")

            dashboard = self.generate_dashboard(

                state.prototype_output,

                state.mock_data_output

            )

            state.dashboard_output = dashboard

            logger.info("Reporter Agent completed successfully.")

        except Exception as ex:

            logger.exception(ex)

            state.error = str(ex)

        return state


    # 2. create_reporter_agent()

    def create_reporter_agent(self):
        """
        Creates Reporter LangGraph workflow.
        """

        workflow = StateGraph(ReporterState)

        workflow.add_node(

            "reporter",

            self.reporter_node

        )

        workflow.add_edge(

            START,

            "reporter"

        )

        workflow.add_edge(

            "reporter",

            END

        )

        return workflow.compile()


    # 3. run_reporter_agent()

    async def run_reporter_agent(

        self,

        prototype_output: dict,

        mock_data_output: dict

    ):

        """
        Executes Reporter Agent.
        """

        agent = self.create_reporter_agent()

        initial_state = ReporterState(

            prototype_output=prototype_output,

            mock_data_output=mock_data_output

        )

        final_state = await agent.ainvoke(

            initial_state

        )

        if final_state.get("error"):

            logger.error(

                final_state["error"]

            )

            return {

                "error":

                    final_state["error"]

            }

        return final_state.get(

            "dashboard_output",

            {}

        )

class ReporterAgent:

    """
    Wrapper class.

    Used by Streamlit and main.py.
    """

    def __init__(self):

        logger.info(

            "ReporterAgent initialized."

        )

        self.engine = ReporterEngine()

    async def process(

        self,

        prototype_output,

        mock_data_output

    ):

        return await self.engine.run_reporter_agent(

            prototype_output,

            mock_data_output

        )

    def generate_dashboard(

        self,

        prototype_output,

        mock_data_output

    ):

        import asyncio

        return asyncio.run(

            self.engine.run_reporter_agent(

                prototype_output,

                mock_data_output

            )

        )



