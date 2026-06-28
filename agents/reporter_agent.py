"""
Reporter Agent - Final agent in the Multi-Agent BI Requirement Analysis System.

Generates professional Business Intelligence reports from requirement analysis,
clarification results, and dashboard prototypes.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.agent_trace import AgentTrace
from utils.llm_helper import get_llm


class ReporterAgent:
    """
    Reporter Agent for generating comprehensive BI reports.
    
    This agent is the final step in the pipeline, producing professional
    HTML reports that summarize requirements, clarifications, and prototypes.
    """

    def __init__(self):
        """Initialize the Reporter Agent with logger, LLM, and reports folder."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        self.llm = get_llm()
        self.trace: Optional[AgentTrace] = None
        
        self.reports_folder = Path("reports")
        self._ensure_reports_folder()
        
        self.logger.info("ReporterAgent initialized")

    def _ensure_reports_folder(self) -> None:
        """Create reports folder if it doesn't exist."""
        try:
            self.reports_folder.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Reports folder ensured at {self.reports_folder}")
        except Exception as e:
            self.logger.error(f"Failed to create reports folder: {e}")
            raise

    def generate_report(
        self,
        requirement_result: dict,
        clarification_result: dict,
        prototype_result: dict,
        run_id: str,
    ) -> str:
        """
        Generate a comprehensive BI report.
        
        Args:
            requirement_result: Result from Requirement Agent
            clarification_result: Result from Clarification Agent
            prototype_result: Result from Prototype Agent
            run_id: Unique identifier for this run
            
        Returns:
            Path to generated HTML report
            
        Raises:
            ValueError: If inputs are invalid
            Exception: On report generation failure
        """
        try:
            self.logger.info(f"Report generation started for run_id: {run_id}")
            self.trace = AgentTrace(agent_name="ReporterAgent", run_id=run_id)
            self.trace.log_start()
            self.trace.log_input({
                "requirement_result": bool(requirement_result),
                "clarification_result": bool(clarification_result),
                "prototype_result": bool(prototype_result),
                "run_id": run_id,
            })
            
            # Validate inputs
            self._validate_inputs(requirement_result, clarification_result, prototype_result, run_id)
            self.trace.log_step("inputs_validated")
            
            # Summarize sections
            requirement_summary = self._summarize_requirements(requirement_result)
            self.trace.log_step("requirement_summarized")
            
            clarification_summary = self._summarize_clarifications(clarification_result)
            self.trace.log_step("clarification_summarized")
            
            prototype_summary = self._summarize_prototype(prototype_result)
            self.trace.log_step("prototype_summarized")
            
            # Generate AI-powered content
            executive_summary = self._generate_executive_summary(
                requirement_summary, clarification_summary, prototype_summary
            )
            self.trace.log_step("executive_summary_generated")
            self.logger.info("Executive summary generated")
            
            recommendations = self._generate_recommendations(
                requirement_summary, clarification_summary, prototype_summary
            )
            self.trace.log_step("recommendations_generated")
            self.logger.info("Recommendations generated")
            
            implementation_notes = self._generate_implementation_notes(
                requirement_summary, clarification_summary, prototype_summary
            )
            self.trace.log_step("implementation_notes_generated")
            
            risks_assumptions = self._generate_risks_assumptions(requirement_summary)
            self.trace.log_step("risks_assumptions_generated")
            
            # Generate HTML report
            html_content = self._generate_html(
                run_id=run_id,
                executive_summary=executive_summary,
                requirement_summary=requirement_summary,
                clarification_summary=clarification_summary,
                prototype_summary=prototype_summary,
                recommendations=recommendations,
                implementation_notes=implementation_notes,
                risks_assumptions=risks_assumptions,
                prototype_result=prototype_result,
            )
            self.trace.log_step("html_generated")
            self.logger.info("HTML report created")
            
            # Save report
            report_path = self._save_report(html_content, run_id)
            self.trace.log_step("report_saved")
            self.logger.info(f"Report saved at {report_path}")
            
            self.trace.log_completion()
            self.logger.info(f"Report generation completed for run_id: {run_id}")
            
            return str(report_path)
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            if self.trace:
                self.trace.log_error(str(e))
            raise

    def _validate_inputs(
        self,
        requirement_result: dict,
        clarification_result: dict,
        prototype_result: dict,
        run_id: str,
    ) -> None:
        """
        Validate input parameters.
        
        Args:
            requirement_result: Result from Requirement Agent
            clarification_result: Result from Clarification Agent
            prototype_result: Result from Prototype Agent
            run_id: Unique identifier
            
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(requirement_result, dict):
            raise ValueError("requirement_result must be a dictionary")
        if not isinstance(clarification_result, dict):
            raise ValueError("clarification_result must be a dictionary")
        if not isinstance(prototype_result, dict):
            raise ValueError("prototype_result must be a dictionary")
        if not isinstance(run_id, str) or not run_id.strip():
            raise ValueError("run_id must be a non-empty string")

    def _summarize_requirements(self, requirement_result: dict) -> Dict[str, Any]:
        """
        Summarize requirement analysis results.
        
        Args:
            requirement_result: Result from Requirement Agent
            
        Returns:
            Dictionary with summarized requirements
        """
        summary = {
            "business_goal": requirement_result.get("business_goal", "Not specified"),
            "kpis": requirement_result.get("kpis", []),
            "measures": requirement_result.get("measures", []),
            "dimensions": requirement_result.get("dimensions", []),
            "filters": requirement_result.get("filters", []),
        }
        return summary

    def _summarize_clarifications(self, clarification_result: dict) -> Dict[str, Any]:
        """
        Summarize clarification responses.
        
        Args:
            clarification_result: Result from Clarification Agent
            
        Returns:
            Dictionary with summarized clarifications
        """
        summary = {
            "questions": clarification_result.get("questions", []),
            "answers": clarification_result.get("answers", []),
            "clarifications": clarification_result.get("clarifications", []),
        }
        return summary

    def _summarize_prototype(self, prototype_result: dict) -> Dict[str, Any]:
        """
        Summarize dashboard prototype details.
        
        Args:
            prototype_result: Result from Prototype Agent
            
        Returns:
            Dictionary with summarized prototype
        """
        summary = {
            "dashboard_name": prototype_result.get("dashboard_name", "Dashboard"),
            "description": prototype_result.get("description", ""),
            "visualizations": prototype_result.get("visualizations", []),
            "chart_data": prototype_result.get("chart_data", []),
        }
        return summary

    def _generate_executive_summary(
        self,
        requirement_summary: Dict[str, Any],
        clarification_summary: Dict[str, Any],
        prototype_summary: Dict[str, Any],
    ) -> str:
        """
        Generate executive summary using LLM.
        
        Args:
            requirement_summary: Summarized requirements
            clarification_summary: Summarized clarifications
            prototype_summary: Summarized prototype
            
        Returns:
            Executive summary text
        """
        try:
            prompt = f"""
            Based on the following BI analysis, generate a concise executive summary (2-3 paragraphs):
            
            Business Goal: {requirement_summary.get('business_goal')}
            KPIs: {', '.join(requirement_summary.get('kpis', []))}
            Measures: {', '.join(requirement_summary.get('measures', []))}
            Dimensions: {', '.join(requirement_summary.get('dimensions', []))}
            
            Clarifications: {len(clarification_summary.get('clarifications', []))} items
            Dashboard: {prototype_summary.get('dashboard_name')}
            
            Focus on the business value and key insights.
            """
            
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            self.logger.warning(f"Failed to generate executive summary via LLM: {e}")
            return "Executive summary generation pending. Please refer to the detailed sections below."

    def _generate_recommendations(
        self,
        requirement_summary: Dict[str, Any],
        clarification_summary: Dict[str, Any],
        prototype_summary: Dict[str, Any],
    ) -> str:
        """
        Generate recommendations using LLM.
        
        Args:
            requirement_summary: Summarized requirements
            clarification_summary: Summarized clarifications
            prototype_summary: Summarized prototype
            
        Returns:
            Recommendations text
        """
        try:
            prompt = f"""
            Based on the following BI analysis, provide 3-5 specific recommendations for implementation:
            
            Business Goal: {requirement_summary.get('business_goal')}
            KPIs: {', '.join(requirement_summary.get('kpis', []))}
            Visualizations Planned: {', '.join(prototype_summary.get('visualizations', []))}
            
            Format as a numbered list.
            """
            
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            self.logger.warning(f"Failed to generate recommendations via LLM: {e}")
            return "Recommendations will be finalized during implementation."

    def _generate_implementation_notes(
        self,
        requirement_summary: Dict[str, Any],
        clarification_summary: Dict[str, Any],
        prototype_summary: Dict[str, Any],
    ) -> str:
        """
        Generate implementation notes using LLM.
        
        Args:
            requirement_summary: Summarized requirements
            clarification_summary: Summarized clarifications
            prototype_summary: Summarized prototype
            
        Returns:
            Implementation notes text
        """
        try:
            prompt = f"""
            Provide implementation notes for building the following dashboard:
            
            Dashboard: {prototype_summary.get('dashboard_name')}
            Description: {prototype_summary.get('description')}
            
            Measures Required: {', '.join(requirement_summary.get('measures', []))}
            Dimensions Required: {', '.join(requirement_summary.get('dimensions', []))}
            
            Include data preparation, refresh frequency, and technical considerations.
            Format as structured notes.
            """
            
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            self.logger.warning(f"Failed to generate implementation notes via LLM: {e}")
            return "Implementation details to be determined during development phase."

    def _generate_risks_assumptions(self, requirement_summary: Dict[str, Any]) -> str:
        """
        Generate risks and assumptions using LLM.
        
        Args:
            requirement_summary: Summarized requirements
            
        Returns:
            Risks and assumptions text
        """
        try:
            prompt = f"""
            Identify potential risks and assumptions for the following BI initiative:
            
            Business Goal: {requirement_summary.get('business_goal')}
            KPIs: {', '.join(requirement_summary.get('kpis', []))}
            Filters: {', '.join(requirement_summary.get('filters', []))}
            
            List 3-4 risks and 2-3 assumptions.
            """
            
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            self.logger.warning(f"Failed to generate risks/assumptions via LLM: {e}")
            return "Risk assessment to be completed in the planning phase."

    def _create_chart(self, chart_data: dict) -> Optional[str]:
        """
        Create a Plotly chart from chart metadata.
        
        Args:
            chart_data: Dictionary containing chart configuration
            
        Returns:
            HTML string of the chart, or None if chart creation fails
        """
        try:
            chart_type = chart_data.get("type", "bar")
            data = chart_data.get("data", {})
            
            if not data:
                return None
            
            if chart_type == "bar":
                fig = px.bar(data, title=chart_data.get("title", ""))
            elif chart_type == "line":
                fig = px.line(data, title=chart_data.get("title", ""))
            elif chart_type == "pie":
                fig = px.pie(data, title=chart_data.get("title", ""))
            else:
                return None
            
            return fig.to_html(include_plotlyjs='cdn', div_id=f"chart_{hash(str(data))}")
        except Exception as e:
            self.logger.warning(f"Failed to create chart: {e}")
            return None

    def _format_section(self, title: str, content: str) -> str:
        """
        Format a report section with HTML styling.
        
        Args:
            title: Section title
            content: Section content
            
        Returns:
            Formatted HTML section
        """
        return f"""
        <div class="section">
            <h2>{self._escape_html(title)}</h2>
            <div class="content">
                {content}
            </div>
        </div>
        """

    def _escape_html(self, text: str) -> str:
        """
        Escape HTML special characters.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        if not isinstance(text, str):
            text = str(text)
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    def _generate_html(
        self,
        run_id: str,
        executive_summary: str,
        requirement_summary: Dict[str, Any],
        clarification_summary: Dict[str, Any],
        prototype_summary: Dict[str, Any],
        recommendations: str,
        implementation_notes: str,
        risks_assumptions: str,
        prototype_result: dict,
    ) -> str:
        """
        Generate professional HTML report.
        
        Args:
            run_id: Run identifier
            executive_summary: Executive summary text
            requirement_summary: Summarized requirements
            clarification_summary: Summarized clarifications
            prototype_summary: Summarized prototype
            recommendations: Recommendations text
            implementation_notes: Implementation notes
            risks_assumptions: Risks and assumptions
            prototype_result: Original prototype result
            
        Returns:
            HTML content as string
        """
        generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build content sections
        kpis_html = "".join([f"<li>{self._escape_html(kpi)}</li>" for kpi in requirement_summary.get("kpis", [])])
        measures_html = "".join([f"<li>{self._escape_html(m)}</li>" for m in requirement_summary.get("measures", [])])
        dimensions_html = "".join([f"<li>{self._escape_html(d)}</li>" for d in requirement_summary.get("dimensions", [])])
        filters_html = "".join([f"<li>{self._escape_html(f)}</li>" for f in requirement_summary.get("filters", [])])
        
        clarifications_html = "".join([
            f"<li>{self._escape_html(c)}</li>" 
            for c in clarification_summary.get("clarifications", [])
        ])
        
        visualizations_html = "".join([
            f"<li>{self._escape_html(v)}</li>" 
            for v in prototype_summary.get("visualizations", [])
        ])
        
        # Generate charts
        charts_html = ""
        for chart_data in prototype_result.get("chart_data", []):
            chart_html = self._create_chart(chart_data)
            if chart_html:
                charts_html += chart_html
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BI Report - {self._escape_html(run_id)}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 30px;
            padding: 20px;
            background: #f9fafb;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .section h2 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.8em;
        }}
        
        .section h3 {{
            color: #764ba2;
            margin-top: 15px;
            margin-bottom: 10px;
            font-size: 1.3em;
        }}
        
        .section p {{
            line-height: 1.6;
            margin-bottom: 10px;
        }}
        
        .section ul {{
            margin-left: 20px;
            margin-bottom: 10px;
        }}
        
        .section li {{
            margin-bottom: 8px;
            line-height: 1.5;
        }}
        
        .card {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            border: 1px solid #e0e0e0;
        }}
        
        .card-title {{
            font-weight: 600;
            color: #667eea;
            margin-bottom: 8px;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            border: 1px solid #e0e0e0;
        }}
        
        .footer {{
            background: #f0f0f0;
            padding: 20px 30px;
            text-align: center;
            border-top: 1px solid #ddd;
            font-size: 0.9em;
            color: #666;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        
        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
            .header h1 {{
                font-size: 1.8em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Business Intelligence Report</h1>
            <p>Run ID: {self._escape_html(run_id)}</p>
        </div>
        
        <div class="content">
            {self._format_section("Executive Summary", f"<p>{self._escape_html(executive_summary)}</p>")}
            
            {self._format_section("Business Goal", f"<p>{self._escape_html(requirement_summary.get('business_goal', 'Not specified'))}</p>")}
            
            <div class="section">
                <h2>Requirements</h2>
                <div class="grid">
                    <div class="card">
                        <div class="card-title">Key Performance Indicators</div>
                        <ul>
                            {kpis_html if kpis_html else "<li>No KPIs specified</li>"}
                        </ul>
                    </div>
                    <div class="card">
                        <div class="card-title">Measures</div>
                        <ul>
                            {measures_html if measures_html else "<li>No measures specified</li>"}
                        </ul>
                    </div>
                    <div class="card">
                        <div class="card-title">Dimensions</div>
                        <ul>
                            {dimensions_html if dimensions_html else "<li>No dimensions specified</li>"}
                        </ul>
                    </div>
                    <div class="card">
                        <div class="card-title">Filters</div>
                        <ul>
                            {filters_html if filters_html else "<li>No filters specified</li>"}
                        </ul>
                    </div>
                </div>
            </div>
            
            {self._format_section("Clarifications", f"<ul>{''.join([f'<li>{self._escape_html(c)}</li>' for c in clarification_summary.get('clarifications', [])])}</ul>" if clarification_summary.get('clarifications') else "<p>No clarifications recorded.</p>")}
            
            <div class="section">
                <h2>Dashboard Prototype</h2>
                <h3>{self._escape_html(prototype_summary.get('dashboard_name', 'Dashboard'))}</h3>
                <p>{self._escape_html(prototype_summary.get('description', ''))}</p>
                <h3>Recommended Visualizations</h3>
                <ul>
                    {visualizations_html if visualizations_html else "<li>No visualizations planned</li>"}
                </ul>
                {"<div class='chart-container'>" + charts_html + "</div>" if charts_html else ""}
            </div>
            
            {self._format_section("Recommendations", f"<p>{self._escape_html(recommendations)}</p>")}
            
            {self._format_section("Implementation Notes", f"<p>{self._escape_html(implementation_notes)}</p>")}
            
            {self._format_section("Risks & Assumptions", f"<p>{self._escape_html(risks_assumptions)}</p>")}
        </div>
        
        <div class="footer">
            <p>Report Generated: {generated_time}</p>
            <p>Run ID: {self._escape_html(run_id)}</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html_content

    def _save_report(self, html_content: str, run_id: str) -> Path:
        """
        Save HTML report to file.
        
        Args:
            html_content: HTML content to save
            run_id: Run identifier
            
        Returns:
            Path to saved report
            
        Raises:
            Exception: If save fails
        """
        try:
            report_path = self.reports_folder / f"report_{run_id}.html"
            
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            self.logger.info(f"Report saved successfully at {report_path}")
            return report_path
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")
            raise
