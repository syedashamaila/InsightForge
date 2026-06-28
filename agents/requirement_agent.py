import json
import logging
from typing import Optional
from langchain_core.messages import HumanMessage

from utils.llm_helper import get_llm
from utils.agent_trace import AgentTrace

logger = logging.getLogger(__name__)


class RequirementAgent:
    """
    First step of the workflow - converts business requirements into structured understanding.
    Acts as a senior Power BI business analyst gathering reporting requirements before development.
    """

    def __init__(self):
        """Initialize the requirement agent with LLM and tracing."""
        self.llm = get_llm()
        self.trace = AgentTrace("RequirementAgent")

    def _get_system_prompt(self) -> str:
        """Return the system prompt for the requirement analyst."""
        return """You are a senior Power BI business analyst with 10+ years of experience gathering and structuring reporting requirements.

Your role is to analyze raw business requirements and convert them into a structured, comprehensive understanding before any prototype or development begins.

When analyzing a business requirement, you MUST extract and structure the following information:

1. **business_objective**: The primary goal or objective the requirement aims to achieve
2. **problem_statement**: The specific problem or gap being addressed
3. **target_users**: Identified user personas or roles who will use the report/dashboard
4. **kpis**: Key Performance Indicators that need to be tracked
5. **measures**: Quantitative metrics to be calculated or tracked
6. **dimensions**: Qualitative attributes for grouping/filtering (e.g., time, geography, department)
7. **filters**: Specific filters or slicers required for user interaction
8. **expected_visuals**: Recommended visualization types (e.g., charts, tables, maps)
9. **drill_down_expectations**: Expected drill-down hierarchies or navigation paths
10. **assumptions**: Assumptions made about data availability, accuracy, or business context
11. **dependencies**: External dependencies (systems, data sources, teams)
12. **missing_information**: Information gaps or unknowns that need clarification
13. **ambiguity_list**: Ambiguous statements or requirements that need clarification
14. **risks**: Identified risks or concerns related to this requirement
15. **acceptance_criteria**: Criteria by which success will be measured

IMPORTANT:
- Do NOT attempt to create SQL, DAX, semantic models, or Power BI files
- Do NOT create mock data or sample datasets
- Your ONLY responsibility is understanding and structuring the requirement
- Return output as valid JSON only
- If certain fields cannot be determined from the requirement, set them to empty strings
- Provide clear, actionable, and business-focused descriptions
- Flag any ambiguities or missing information for clarification

Return ONLY a valid JSON object with the above fields. No additional text or formatting."""

    def analyze_requirement(
        self,
        business_requirement: str,
        business_context: str = ""
    ) -> dict:
        """
        Analyze a business requirement and extract structured understanding.
        
        Args:
            business_requirement: The raw business requirement in natural language
            business_context: Optional additional context about the business environment
            
        Returns:
            Dictionary containing structured requirement analysis as JSON
            
        Raises:
            ValueError: If LLM response is invalid or cannot be parsed
            Exception: For other processing errors
        """
        try:
            self.trace.start_operation("analyze_requirement")
            logger.info(f"Starting requirement analysis")
            
            # Build the user message
            user_message = business_requirement
            if business_context:
                user_message = f"""Business Context:
{business_context}

Business Requirement:
{business_requirement}"""

            self.trace.log_input({
                "business_requirement": business_requirement,
                "business_context": business_context
            })

            # Create messages for the LLM
            messages = [HumanMessage(content=user_message)]

            # Call the LLM with system prompt
            response = self.llm.invoke(
                messages,
                system=self._get_system_prompt()
            )

            # Extract the response content
            response_text = response.content.strip()
            self.trace.log_output({"raw_response": response_text})

            # Parse JSON response
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                # Try to extract JSON from the response if it contains extra text
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError(f"LLM response is not valid JSON: {response_text}")

            # Validate required fields
            required_fields = [
                "business_objective", "problem_statement", "target_users",
                "kpis", "measures", "dimensions", "filters", "expected_visuals",
                "drill_down_expectations", "assumptions", "dependencies",
                "missing_information", "ambiguity_list", "risks", "acceptance_criteria"
            ]

            for field in required_fields:
                if field not in result:
                    result[field] = ""
                    logger.warning(f"Field '{field}' missing from LLM response, set to empty string")

            self.trace.end_operation(
                status="success",
                output_summary={
                    "has_kpis": bool(result.get("kpis")),
                    "has_ambiguities": bool(result.get("ambiguity_list")),
                    "has_risks": bool(result.get("risks")),
                    "missing_info_count": len(str(result.get("missing_information", "")).split(","))
                }
            )

            logger.info("Requirement analysis completed successfully")
            return result

        except Exception as e:
            logger.error(f"Error during requirement analysis: {str(e)}", exc_info=True)
            self.trace.end_operation(
                status="error",
                error=str(e)
            )
            raise

    def get_trace_data(self) -> dict:
        """Get the trace data for this operation."""
        return self.trace.get_data()


# Export function for orchestrator integration
def analyze_business_requirement(
    business_requirement: str,
    business_context: str = ""
) -> dict:
    """
    Standalone function to analyze a business requirement.
    This is the entry point for the orchestrator.
    
    Args:
        business_requirement: The raw business requirement
        business_context: Optional business context
        
    Returns:
        Structured requirement analysis as JSON dictionary
    """
    agent = RequirementAgent()
    return agent.analyze_requirement(business_requirement, business_context)
