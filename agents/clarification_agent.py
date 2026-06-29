"""
Clarification Agent - Validates and clarifies BI requirements before development.

This agent reviews the structured output from requirement_agent.py and identifies:
- Unclear, incomplete, or conflicting requirements
- Missing business information
- Ambiguous terminology
- Dependencies and risks

Returns structured JSON with clarification questions, assumptions, risks, and readiness assessment.
"""

import json
import logging
from typing import Any
from langchain_core.messages import BaseMessage, HumanMessage
#from langchain_openai import ChatOpenAI
from utils.llm_helper import get_llm
llm = get_llm()
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


class ClarificationAgent:
    """
    Clarification Agent class for requirement validation and clarification.
    
    Initializes with shared LLM and provides process() method for requirement analysis.
    """
    
    def __init__(self):
        """Initialize the clarification agent with shared LLM."""
        self.llm = get_llm()
    
    def clarify(self, requirement_result):
        return self.process(requirement_result)

    def process(self, requirement_json: dict | str) -> dict[str, Any]:
        """
        Process requirements through clarification analysis.
        
        Args:
            requirement_json: Structured requirement output from requirement_agent
            
        Returns:
            Dictionary containing clarification analysis and recommendations
        """
        return process_clarification(requirement_json)


class ClarificationQuestion(BaseModel):
    """Model for a single clarification question."""
    question: str = Field(description="The clarification question for the client")
    priority: str = Field(description="Priority level: High, Medium, or Low")
    related_area: str = Field(description="Area of requirement this relates to (e.g., 'KPI Definition', 'Dimension', 'Filter', etc.)")
    impact: str = Field(description="Why this clarification is important")


class AssumptionConfirmation(BaseModel):
    """Model for assumptions that need confirmation."""
    assumption: str = Field(description="The assumption made from requirements")
    confidence_level: str = Field(description="How confident are we in this assumption: High, Medium, Low")
    mitigation: str = Field(description="How this assumption will be validated")


class BusinessRisk(BaseModel):
    """Model for identified business risks."""
    risk: str = Field(description="Description of the identified risk")
    severity: str = Field(description="Risk severity: High, Medium, Low")
    mitigation_strategy: str = Field(description="Suggested approach to mitigate this risk")


class ClarificationResponse(BaseModel):
    """Model for the complete clarification agent response."""
    requirement_complete: bool = Field(description="Whether the requirement is sufficiently complete to proceed")
    requirement_completeness_summary: str = Field(description="Explanation of why requirement is complete or incomplete")
    clarification_questions: list[ClarificationQuestion] = Field(description="List of clarification questions for the client")
    assumptions_to_confirm: list[AssumptionConfirmation] = Field(description="Assumptions extracted from requirements that need confirmation")
    business_risks: list[BusinessRisk] = Field(description="Identified business risks and mitigation strategies")
    suggested_improvements: list[str] = Field(description="Suggested improvements or clarifications to the requirements")
    readiness_score: int = Field(description="Overall readiness score from 0-100")
    recommendation: str = Field(description="Recommendation: 'Proceed to Prototype' or 'Clarify First'")
    next_steps: list[str] = Field(description="Recommended next steps")


def process_clarification(requirement_json: dict | str) -> dict[str, Any]:
    """
    Process requirements through the clarification agent.
    
    Args:
        requirement_json: Structured requirement output from requirement_agent
        
    Returns:
        Dictionary containing clarification analysis and recommendations
    """
    try:
        # Parse input if string
        if isinstance(requirement_json, str):
            requirements = json.loads(requirement_json)
        else:
            requirements = requirement_json
            
        logger.info("Processing requirement clarification")
        
        """# Initialize LLM
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            timeout=60
        )
        """
        # Create clarification prompt
        clarification_prompt = ChatPromptTemplate.from_template("""You are a senior BI consultant reviewing business requirements before development.

Your task is to analyze the following requirement specification and identify:
1. Unclear, incomplete, or conflicting requirements
2. Missing business context or information
3. Ambiguous terminology that needs clarification
4. Hidden assumptions and dependencies
5. Business risks and gaps
6. Overall readiness for prototype development

REQUIREMENT SPECIFICATION:
{requirement_spec}

Analyze thoroughly and provide your assessment in the specified JSON format. Be thorough but pragmatic - do not invent questions if the requirement is sufficiently clear. For each question, justify why it's important and assess its priority.

Return a JSON object with the following structure:
{{
    "requirement_complete": boolean,
    "requirement_completeness_summary": "detailed explanation",
    "clarification_questions": [
        {{
            "question": "specific question",
            "priority": "High/Medium/Low",
            "related_area": "affected area",
            "impact": "why this matters"
        }}
    ],
    "assumptions_to_confirm": [
        {{
            "assumption": "assumed statement",
            "confidence_level": "High/Medium/Low",
            "mitigation": "how to validate"
        }}
    ],
    "business_risks": [
        {{
            "risk": "description",
            "severity": "High/Medium/Low",
            "mitigation_strategy": "mitigation approach"
        }}
    ],
    "suggested_improvements": ["improvement 1", "improvement 2"],
    "readiness_score": 0-100,
    "recommendation": "Proceed to Prototype or Clarify First",
    "next_steps": ["step 1", "step 2"]
}}
""")
        
        # Format requirement specification
        requirement_spec = json.dumps(requirements, indent=2)
        
        # Create parser
        parser = JsonOutputParser(pydantic_object=ClarificationResponse)
        
        # Build chain
        chain = clarification_prompt | llm | parser
        
        # Execute analysis
        result = chain.invoke({"requirement_spec": requirement_spec})
        
        logger.info(f"Clarification analysis complete. Readiness score: {result.get('readiness_score', 'N/A')}")
        
        # Convert to dictionary for serialization
        return result.model_dump() if hasattr(result, 'model_dump') else result
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in requirement input: {e}")
        raise
    except Exception as e:
        logger.error(f"Error in clarification processing: {e}")
        raise


def run_clarification_agent(state: dict) -> dict:
    """
    Agent node function for LangGraph orchestrator.
    
    Args:
        state: Current state from orchestrator containing requirement data
        
    Returns:
        Updated state with clarification analysis
    """
    logger.info("Starting Clarification Agent")
    
    # Extract requirement from state
    requirement_data = state.get("requirement_output") or state.get("requirements")
    
    if not requirement_data:
        raise ValueError("No requirement data found in state")
    
    # Process clarification
    clarification_result = process_clarification(requirement_data)
    
    # Log results
    logger.info(f"Recommendation: {clarification_result.get('recommendation')}")
    logger.info(f"Readiness Score: {clarification_result.get('readiness_score')}")
    
    # Update state
    return {
        "clarification_output": clarification_result,
        "agent_log": f"Clarification Agent completed. Readiness: {clarification_result.get('readiness_score')}/100"
    }


if __name__ == "__main__":
    # Example usage for testing
    sample_requirement = {
        "kpis": [{"name": "Revenue", "definition": "Total sales revenue"}],
        "dimensions": [{"name": "Date", "type": "date"}],
        "filters": [{"name": "Region", "values": ["US", "EU"]}],
        "visuals": [{"type": "bar chart"}]
    }
    
    result = process_clarification(sample_requirement)
    print(json.dumps(result, indent=2))
