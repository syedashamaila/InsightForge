import json
import logging
from typing import Dict, List, Any
from dataclasses import dataclass, asdict, field
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RequirementContext:
    """Data class for BI requirement context."""
    dashboard_title: str = ""
    business_objective: str = ""
    business_domain: str = ""
    target_users: List[str] = field(default_factory=list)
    kpis: List[str] = field(default_factory=list)
    measures: List[str] = field(default_factory=list)
    dimensions: List[str] = field(default_factory=list)
    filters: List[str] = field(default_factory=list)
    business_questions: List[str] = field(default_factory=list)
    fact_tables: List[str] = field(default_factory=list)
    dimension_tables: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)


class RequirementAgent:
    """
    AI-powered agent for converting natural language BI requirements
    into structured business intelligence specifications using Gemini.
    """

    SYSTEM_PROMPT = (
        "You are a Senior Business Intelligence Solution Architect with extensive experience "
        "in Power BI, Microsoft Fabric, Azure, SQL, dimensional modeling, data warehousing, "
        "dashboard design and business analysis.\n"
        "Your responsibility is to analyze business reporting requirements and convert them "
        "into structured BI specifications.\n"
        "You MUST respond ONLY a valid JSON object.\n"
        "Do not write markdown, explanations, or any text outside the JSON object.\n"
        "Do not use ```json.\n"
        "The first character of your response must be '{' and the last character must be '}'.\n"
        "Do not include markdown.\n"
        "Do not explain your reasoning.\n"
        "Do not wrap the response inside code blocks."
    )

    REQUIRED_FIELDS = {
        "dashboard_title",
        "business_objective",
        "business_domain",
        "target_users",
        "kpis",
        "measures",
        "dimensions",
        "filters",
        "business_questions",
        "fact_tables",
        "dimension_tables",
        "relationships",
        "assumptions",
        "success_criteria",
    }

    def __init__(self, model_name: str = "gemini-1.5-flash") -> None:
        """
        Initialize the requirement agent.

        Args:
            model_name: Gemini model name to use for analysis
        """
        logger.info(f"Initializing RequirementAgent with model: {model_name}")
        self.model_name = model_name
        self.specification: RequirementContext = RequirementContext()

    def analyze_requirement(self, requirement: str) -> Dict[str, Any]:
        """
        Convert natural language business requirement into structured specification using Gemini.

        Args:
            requirement: Natural language business requirement string

        Returns:
            Dictionary containing structured BI specification

        Raises:
            ValueError: If requirement is invalid
            Exception: For LLM or processing errors
        """
        try:
            logger.info("Starting requirement analysis")
            
            self._validate_input(requirement)
            prompt = self._build_prompt(requirement)
            response_text = self._call_llm(prompt)
            parsed_response = self._parse_response(response_text)
            self._validate_response(parsed_response)
            self._populate_dataclass(parsed_response)
            
            result = self._convert_to_dict()

            logger.info("Requirement analysis completed successfully")
            logger.debug(result)

            return result
            

        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            raise
        except json.JSONDecodeError as je:
            logger.error(f"JSON parsing error: {str(je)}")
            raise Exception(f"Failed to parse LLM response as JSON: {str(je)}")
        except Exception as ex:
            logger.error(f"Unexpected error during requirement analysis: {str(ex)}")
            raise Exception(f"Failed to analyze requirement: {str(ex)}")

    def _validate_input(self, requirement: str) -> None:
        """
        Validate the input requirement.

        Args:
            requirement: Natural language business requirement string

        Raises:
            ValueError: If requirement is empty or invalid type
        """
        if not requirement or not isinstance(requirement, str):
            raise ValueError("Requirement must be a non-empty string")
        
        if len(requirement.strip()) == 0:
            raise ValueError("Requirement cannot be only whitespace")
        
        logger.debug(f"Input requirement validated (length: {len(requirement)})")

    def _build_prompt(self, requirement: str) -> str:
        """
        Build the prompt to send to Gemini.

        Args:
            requirement: Natural language business requirement string

        Returns:
            Formatted prompt for Gemini
        """
        prompt = (
            f"Analyze the following BI requirement and return a structured JSON specification:\n\n"
            f"Determine:\n\n"
            f"1. Business Objective\n"
            f"2. Dashboard Title\n"
            f"3. Intended User\n"
            f"4. KPIs\n"
            f"5. Measures\n"
            f"6. Dimensions\n"
            f"7. Filters\n"
            f"8. Business Questions\n"
            f"9. Fact Tables\n"
            f"10. Dimension Tables\n"
            f"11. Relationships\n"
            f"12. Assumptions\n"
            f"13. Success Criteria\n\n"
            f"Infer responsible values when the user does not explicitly provide them"
            f"{requirement}\n\n"
            f"Return ONLY valid JSON (no markdown, no code blocks, no explanations) "
            f"with the following schema:\n"
            f"{{\n"
            f'  "dashboard_title": "",\n'
            f'  "business_objective": "",\n'
            f'  "business_domain": "",\n'
            f'  "target_users": [],\n'
            f'  "kpis": [],\n'
            f'  "measures": [],\n'
            f'  "dimensions": [],\n'
            f'  "filters": [],\n'
            f'  "business_questions": [],\n'
            f'  "fact_tables": [],\n'
            f'  "dimension_tables": [],\n'
            f'  "relationships": [],\n'
            f'  "assumptions": [],\n'
            f'  "success_criteria": []\n'
            f"}}"
           
        )
        logger.debug("Prompt built successfully")
        return prompt

    def _call_llm(self, prompt: str) -> str:
        """
        Call the Gemini LLM with the given prompt.

        Args:
            prompt: The prompt to send to Gemini

        Returns:
            Response text from Gemini

        Raises:
            Exception: If LLM call fails
        """
        try:
            logger.debug(f"Calling Gemini model: {self.model_name}")
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=self.SYSTEM_PROMPT
            )
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "response_mime_type": "application/json",
                }
            )

            response_text = response.text.strip()
            logger.debug("LLM call completed successfully")
            return response_text
        except Exception as ex:
            logger.error(f"Error calling LLM: {str(ex)}")
            raise Exception(f"Failed to call Gemini LLM: {str(ex)}")

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse the JSON response from Gemini.

        Args:
            response_text: Raw response text from Gemini

        Returns:
            Parsed JSON as dictionary

        Raises:
            json.JSONDecodeError: If response is not valid JSON
        """
        try:
            parsed = json.loads(response_text)
            logger.debug("Response parsed successfully as JSON")
            return parsed
        except json.JSONDecodeError as je:
            logger.error(f"Invalid JSON in LLM response: {response_text[:200]}")
            raise

    def _validate_response(self, response: Dict[str, Any]) -> None:
        """
        Validate that all required fields are present in the response.

        Args:
            response: Parsed JSON response from Gemini

        Raises:
            ValueError: If required fields are missing
        """
        missing_fields = self.REQUIRED_FIELDS - set(response.keys())
        if missing_fields:
            logger.warning(f"Missing fields in LLM response: {missing_fields}")
            # Populate missing fields with defaults instead of raising
            for field in missing_fields:
                if field in ["target_users", "kpis", "measures", "dimensions", "filters",
                            "business_questions", "fact_tables", "dimension_tables",
                            "relationships", "assumptions", "success_criteria"]:
                    response[field] = []
                else:
                    response[field] = ""
        
        logger.debug("Response validation completed")

    def _populate_dataclass(self, response: Dict[str, Any]) -> None:
        """
        Populate the RequirementContext dataclass from parsed response.

        Args:
            response: Parsed JSON response from Gemini
        """
        try:
            self.specification = RequirementContext(
                dashboard_title=str(response.get("dashboard_title", "")),
                business_objective=str(response.get("business_objective", "")),
                business_domain=str(response.get("business_domain", "")),
                target_users=self._ensure_list(response.get("target_users", [])),
                kpis=self._ensure_list(response.get("kpis", [])),
                measures=self._ensure_list(response.get("measures", [])),
                dimensions=self._ensure_list(response.get("dimensions", [])),
                filters=self._ensure_list(response.get("filters", [])),
                business_questions=self._ensure_list(response.get("business_questions", [])),
                fact_tables=self._ensure_list(response.get("fact_tables", [])),
                dimension_tables=self._ensure_list(response.get("dimension_tables", [])),
                relationships=self._ensure_list(response.get("relationships", [])),
                assumptions=self._ensure_list(response.get("assumptions", [])),
                success_criteria=self._ensure_list(response.get("success_criteria", [])),
            )
            logger.debug("Dataclass populated successfully")
        except Exception as ex:
            logger.error(f"Error populating dataclass: {str(ex)}")
            raise

    def _ensure_list(self, value: Any) -> List[str]:
        """
        Ensure value is a list of strings.

        Args:
            value: Value to convert to list

        Returns:
            List of strings
        """
        if isinstance(value, list):
            return [str(item) for item in value]
        elif isinstance(value, str):
            return [value] if value else []
        else:
            return []

    def _convert_to_dict(self) -> Dict[str, Any]:
        """
        Convert specification to dictionary.

        Returns:
            Dictionary representation of the specification

        Raises:
            Exception: If conversion fails
        """
        try:
            result = asdict(self.specification)
            logger.debug("Specification converted to dictionary successfully")
            return result
        except Exception as ex:
            logger.error(f"Error converting specification to dictionary: {str(ex)}")
            raise


def process_requirement(requirement: str) -> Dict[str, Any]:
    """
    Process a natural language BI requirement and return structured specification.

    This is the main entry point for requirement processing.

    Args:
        requirement: Natural language business requirement

    Returns:
        Dictionary containing structured BI specification

    Raises:
        ValueError: If requirement is invalid
        Exception: For processing errors
    """
    try:
        logger.info("Processing requirement via process_requirement")
        agent = RequirementAgent()
        return agent.analyze_requirement(requirement)
    except Exception as ex:
        logger.error(f"Error in process_requirement: {str(ex)}")
        raise
