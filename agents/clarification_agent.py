import logging
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
from pathlib import Path


#==================================================================
# Clarification Agent Configuration
#==================================================================

READY_CONFIDENCE_THRESHOLD = 70  # Confidence % above which we consider the requirement clarified
NEEDS_CLARIFICATION_THRESHOLD = 40  # Confidence % below which we require user input

FOLLOW_UP_CONFIDENCE_THRESHOLD = 80  # Confidence % below which we generate follow-up questions
MAX_FOLLOW_UP_QUESTIONS = 3  # Limit the number of follow-up questions to avoid overwhelming the user

MISSING_INFO_PENALTY = 15  # Confidence penalty for each missing information item
AMBIGUITY_PENALTY = 10  # Confidence penalty for each ambiguity detected
CONFLICT_PENALTY = 20  # Confidence penalty for each conflict detected
ASSUMPTION_PENALTY = 5  # Confidence penalty for each assumption made    

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BusinessTerminology(Enum):
    """Normalized business terminology mappings.
    
    TODO: Load from resources/business_terms.json in production
    
    This enum defines the standard business terminology used for normalization.
    Future: Replace with external configuration loading to support multiple
    domain vocabularies and organizational terminology standards.
    """
    REVENUE = {"revenue", "sales", "turnover", "income"}
    CUSTOMER = {"customer", "client", "account", "consumer"}
    PRODUCT = {"product", "item", "sku", "offering"}
    ORDER = {"order", "transaction", "purchase", "sale"}
    METRIC = {"metric", "measure", "kpi", "indicator"}
    FILTER = {"filter", "slice", "segment", "drill-down"}
    DIMENSION = {"dimension", "attribute", "field", "category"}
    
    @classmethod
    def load_from_config(cls, config_path: Optional[str] = None) -> Dict[str, set]:
        """
        Load terminology mappings from external config file.
        
        Future: Implement loading from resources/business_terms.json
        
        Args:
            config_path: Path to JSON config file
            
        Returns:
            Dictionary of terminology mappings
        """
        # TODO: Implement config file loading
        # For now, return enum values
        return {cat.name: cat.value for cat in cls}

class ClarificationStatus(Enum):
    """Status of the clarification process."""
    PENDING = "pending"
    NEEDS_CLARIFICATION = "needs_clarification"
    COMPLETE = "complete"
    ERROR = "error"

@dataclass
class ConversationEntry:
    """Represents a single turn in the clarification conversation."""
    timestamp: datetime
    question: str
    answer: Optional[str] = None
    question_type: str = "follow_up"  # follow_up, validation, assumption
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "question": self.question,
            "answer": self.answer,
            "question_type": self.question_type
        }


@dataclass
class ClarifiedRequirement:
    """
    Represents the final clarified business requirement.
    
    This is the ONLY object that downstream agents consume.
    Contains purely business requirement information.
    
    NOTE: Detailed business decomposition (measures, dimensions, KPI calculations,
    schema design) is NOT the responsibility of ClarificationAgent.
    Those tasks belong to RequirementAgent.
    
    The ClarifiedRequirement contains:
    - Business intent and objective (WHAT problem to solve)
    - High-level business domain
    - Target audience
    - Conversation summary (clarified discussion)
    - Any noted assumptions
    - Missing information or ambiguities
    
    The RequirementAgent will consume this and perform detailed decomposition.
    """
    original_request: str
    clarified_request: str
    conversation_summary: str
    business_domain: str
    business_objective: str
    audience: List[str]
    reporting_grain: str
    assumptions: List[str]
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.original_request or not self.original_request.strip():
            raise ValueError("original_request cannot be empty")
        if not self.clarified_request or not self.clarified_request.strip():
            raise ValueError("clarified_request cannot be empty")
        if not self.business_objective or not self.business_objective.strip():
            raise ValueError("business_objective cannot be empty")
        if not self.conversation_summary or not self.conversation_summary.strip():
            raise ValueError("conversation_summary cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "original_request": self.original_request,
            "clarified_request": self.clarified_request,
            "conversation_summary": self.conversation_summary,
            "business_domain": self.business_domain,
            "business_objective": self.business_objective,
            "audience": self.audience,
            "reporting_grain": self.reporting_grain,
            "assumptions": self.assumptions
        }


@dataclass
class ClarificationResult:
    """
    Represents the complete output of the ClarificationAgent.
    
    Contains the clarified requirement plus metadata for logging,
    debugging, and auditing.
    
    Stateless architecture:
    - ClarificationAgent is a stateless function
    - Each call produces a fresh result
    - UI (Streamlit) manages conversation state and calls agent iteratively
    - If needs_user_input=True, UI collects answers and calls agent again
    """
    clarified_requirement: ClarifiedRequirement
    needs_user_input: bool = False
    follow_up_questions: List[str] = field(default_factory=list)
    missing_information: List[str] = field(default_factory=list)
    ambiguities_detected: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    conversation_history: List[ConversationEntry] = field(default_factory=list)
    ready_for_requirement_agent: bool = False
    status: ClarificationStatus = ClarificationStatus.PENDING
    processing_timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate required fields."""
        if not isinstance(self.clarified_requirement, ClarifiedRequirement):
            raise ValueError("clarified_requirement must be a ClarifiedRequirement instance")
        if not 0 <= self.confidence_score <= 100:
            raise ValueError("confidence_score must be between 0 and 100")
        if not isinstance(self.status, ClarificationStatus):
            raise ValueError("status must be a ClarificationStatus enum")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "clarified_requirement": self.clarified_requirement.to_dict(),
            "needs_user_input": self.needs_user_input,
            "follow_up_questions": self.follow_up_questions,
            "missing_information": self.missing_information,
            "ambiguities_detected": self.ambiguities_detected,
            "confidence_score": self.confidence_score,
            "conversation_history": [entry.to_dict() for entry in self.conversation_history],
            "ready_for_requirement_agent": self.ready_for_requirement_agent,
            "status": self.status.value,
            "processing_timestamp": self.processing_timestamp.isoformat()
        }


class ClarificationAgent:
    """
    Production-quality ClarificationAgent.
    
    Acts as a Senior Business Analyst whose responsibility is to:
    - Understand the user's business requirement
    - Identify ambiguity, conflicts, and missing information
    - Ask intelligent follow-up questions (human-in-the-loop)
    - Build a clarified business requirement
    
    NOT the responsibility of ClarificationAgent:
    - Detailed business decomposition
    - Identifying fact tables, dimensions, measures
    - Designing star/snowflake schema
    - Calculating KPIs
    - Data model design
    
    Stateless Architecture:
    - Each call to run() is independent
    - No internal conversation state maintained between calls
    - UI layer (Streamlit) manages conversation flow
    - To continue clarification, UI calls run() again with updated context
    
    Public interface:
        run(user_request: str, 
            previous_clarification: Optional[ClarificationResult] = None,
            user_answers: Optional[List[str]] = None) -> ClarificationResult
    """
    
    def __init__(self):
        """Initialize the ClarificationAgent."""
        self.logger = logging.getLogger(self.__class__.__name__)
        # Terminology normalizer
        self._term_mappings = self._build_terminology_mappings()
    
    def run(
        self,
        user_request: str,
        previous_clarification: Optional[ClarificationResult] = None,
        user_answers: Optional[List[str]] = None
    ) -> ClarificationResult:
        """
        Main entry point for the ClarificationAgent (stateless).
        
        Processes raw user request and returns a ClarificationResult
        with a clarified requirement.
        
        Stateless Architecture:
        - Call 1: run(user_request) -> generates follow-up questions
        - UI displays questions and collects answers
        - Call 2: run(user_request, previous_clarification, user_answers) -> refines clarification
        
        Args:
            user_request: Natural language business requirement
            previous_clarification: Result from previous clarification step (optional)
            user_answers: User's answers to previous follow-up questions (optional)
            
        Returns:
            ClarificationResult with clarified requirement and next steps
            
        Raises:
            ValueError: If input is invalid
        """
        self.logger.info(f"ClarificationAgent processing request: {user_request[:100]}...")
        
        try:
            # Step 1: Validate input
            self._validate_input(user_request)
            
            # Step 2: Rebuild context from previous state + new answers (if available)
            clarification_context = self._rebuild_context(
                user_request, previous_clarification, user_answers
            )
            
            # Step 3: Analyze request
            analysis = self._analyse_request(user_request)
            
            # Step 4: Detect issues (independent component for LLM replacement)
            missing_info = self._detect_missing_information(analysis)
            conflicts = self._detect_conflicts(analysis)
            ambiguities = self._detect_ambiguities(analysis)
            
            # Step 5: Normalize terminology (independent component for LLM replacement)
            normalized = self._normalize_business_terms(analysis)
            
            # Step 6: Generate assumptions (independent component for LLM replacement)
            assumptions = self._generate_assumptions(normalized, missing_info)
            
            # Step 7: Calculate confidence to decide next action
            confidence = self._calculate_confidence(
                missing_info, assumptions, ambiguities, conflicts
            )
            
            # Step 8: Generate follow-up questions if needed (independent component for LLM replacement)
            follow_up_questions = []
            needs_input = False
            if confidence < FOLLOW_UP_CONFIDENCE_THRESHOLD:
                follow_up_questions = self._generate_follow_up_questions(
                    normalized, missing_info, ambiguities
                )
                needs_input = len(follow_up_questions) > 0
            
            # Step 9: Build clarified requirement
            clarified_req = self._build_clarified_requirement(
                user_request, normalized, assumptions, missing_info, ambiguities
            )
            
            # Step 10: Determine status and readiness
            status, ready_for_downstream = self._determine_readiness(
                confidence, needs_input, missing_info
            )
            
            # Step 11: Build and return result
            result = self._build_result(
                clarified_req, confidence, follow_up_questions,
                missing_info, ambiguities, assumptions, status, needs_input, ready_for_downstream
            )
            
            self.logger.info(
                f"Clarification processing complete. Status: {status}. "
                f"Confidence: {confidence}%. Needs input: {needs_input}. "
                f"Ready for RequirementAgent: {ready_for_downstream}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error during clarification: {str(e)}", exc_info=True)
            raise
    
    def _rebuild_context(
        self,
        user_request: str,
        previous_clarification: Optional[ClarificationResult],
        user_answers: Optional[List[str]]
    ) -> Dict[str, Any]:
        """
        Rebuild clarification context from previous state and new answers.
        
        Similar to LangGraph agent pattern: rebuild state from scratch.
        
        Args:
            user_request: Original user request
            previous_clarification: Previous clarification result
            user_answers: User's answers to follow-up questions
            
        Returns:
            Context dictionary for this clarification round
        """
        self.logger.debug("Rebuilding clarification context...")
        
        context = {
            "original_request": user_request,
            "previous_questions": [],
            "previous_answers": user_answers or [],
            "has_previous_context": previous_clarification is not None
        }
        
        if previous_clarification:
            context["previous_questions"] = previous_clarification.follow_up_questions
            context["previous_confidence"] = previous_clarification.confidence_score
            context["previous_ambiguities"] = previous_clarification.ambiguities_detected
            self.logger.debug(
                f"Restored context from previous clarification. "
                f"Questions answered: {len(user_answers or [])}"
            )
        
        return context
    
    def _validate_input(self, user_request: str) -> None:
        """
        Validate input request.
        
        Args:
            user_request: User's natural language request
            
        Raises:
            ValueError: If input is invalid
        """
        if not user_request or not isinstance(user_request, str):
            raise ValueError("user_request must be a non-empty string")
        
        if len(user_request.strip()) < 10:
            raise ValueError("user_request is too short to analyze")
        
        self.logger.debug(f"Input validation passed for: {user_request[:50]}...")
    
    def _analyse_request(self, user_request: str) -> Dict[str, Any]:
        """
        Analyze the user's request to extract business information.
        
        NOTE: This analysis focuses on BUSINESS INTENT, not technical details.
        
        Responsibility: Identify WHAT the business is trying to achieve.
        NOT: How to design the schema, identify measures/dimensions, etc.
        
        Args:
            user_request: User's natural language request
            
        Returns:
            Dictionary containing analysis results
        """
        self.logger.info("Analyzing business request...")
        
        analysis = {
            "original_text": user_request,
            "business_domain": self._infer_business_domain(user_request),
            "business_intent": self._extract_business_intent(user_request),
            "business_objective": self._extract_business_objective(user_request),
            "target_audience": self._infer_audience(user_request),
            "reporting_grain": self._infer_reporting_grain(user_request),
            # NOTE: NOT extracting measures, dimensions, KPIs
            # Those are RequirementAgent responsibilities
        }
        
        self.logger.debug(f"Analysis result: {analysis}")
        return analysis
    
    def _extract_business_intent(self, text: str) -> str:
        """
        Extract the primary business intent from the request.
        
        Examples:
        - "understand sales performance"
        - "monitor customer churn"
        - "identify regional growth opportunities"
        
        Args:
            text: User's request text
            
        Returns:
            Business intent as a phrase
        """
        intent_patterns = [
            ("understand", "Understand"),
            ("analyze", "Analyze"),
            ("monitor", "Monitor"),
            ("track", "Track"),
            ("identify", "Identify"),
            ("measure", "Measure"),
            ("optimize", "Optimize"),
            ("compare", "Compare"),
            ("visualize", "Visualize"),
            ("explore", "Explore"),
        ]
        
        text_lower = text.lower()
        for pattern, intent in intent_patterns:
            if pattern in text_lower:
                self.logger.debug(f"Business intent: {intent}")
                return intent
        
        self.logger.debug("Business intent: Analyze")
        return "Analyze"
    
    def _infer_business_domain(self, text: str) -> str:
        """Infer business domain from request."""
        text_lower = text.lower()
        
        domains = {
            "sales": ["sales", "revenue", "order", "customer", "product"],
            "finance": ["budget", "revenue", "expense", "profit", "cost", "accounting"],
            "marketing": ["campaign", "lead", "conversion", "roi", "acquisition"],
            "hr": ["employee", "recruitment", "attrition", "payroll", "performance"],
            "inventory": ["stock", "warehouse", "inventory", "sku", "supplier"],
            "general": []
        }
        
        for domain, keywords in domains.items():
            if any(keyword in text_lower for keyword in keywords):
                self.logger.debug(f"Inferred domain: {domain}")
                return domain
        
        self.logger.debug("Using default domain: general")
        return "general"
    
    def _extract_business_objective(self, text: str) -> str:
        """Extract primary business objective from request."""
        objective_keywords = [
            ("analyze", "Analyze"),
            ("monitor", "Monitor"),
            ("track", "Track"),
            ("optimize", "Optimize"),
            ("identify", "Identify"),
            ("measure", "Measure"),
            ("report", "Report"),
            ("dashboard", "Create dashboard"),
            ("build", "Build"),
            ("create", "Create"),
        ]
        
        text_lower = text.lower()
        for keyword, objective in objective_keywords:
            if keyword in text_lower:
                self.logger.debug(f"Extracted objective: {objective}")
                return objective
        
        self.logger.debug("Using default objective: Analyze")
        return "Analyze"
    
    def _infer_audience(self, text: str) -> List[str]:
        """Infer target audience from request."""
        audience_keywords = {
            "executive": ["cfo", "ceo", "executive", "board", "leadership"],
            "manager": ["manager", "director", "supervisor"],
            "analyst": ["analyst", "data team"],
            "operations": ["operations", "ops"],
            "sales": ["sales", "sales team"],
        }
        
        text_lower = text.lower()
        audience = []
        
        for role, keywords in audience_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                audience.append(role)
        
        if not audience:
            audience = ["general"]
        
        self.logger.debug(f"Inferred audience: {audience}")
        return audience
    
    def _infer_reporting_grain(self, text: str) -> str:
        """Infer reporting grain (daily, monthly, etc.)."""
        grain_keywords = {
            "hourly": ["hourly", "hour-by-hour"],
            "daily": ["daily", "day-by-day", "each day"],
            "weekly": ["weekly", "week-by-week"],
            "monthly": ["monthly", "month-by-month", "per month"],
            "quarterly": ["quarterly", "quarter-by-quarter"],
            "yearly": ["yearly", "annual", "per year"],
        }
        
        text_lower = text.lower()
        for grain, keywords in grain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                self.logger.debug(f"Inferred grain: {grain}")
                return grain
        
        self.logger.debug("Using default grain: daily")
        return "daily"
        
    def _detect_missing_information(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Detect missing business information.
        
        NOTE: This focuses on BUSINESS-level missing information, not technical details.
        
        Do NOT check for measures, dimensions, KPIs (RequirementAgent responsibility).
        
        Instead check for:
        - Business problem not clearly stated
        - Target audience not identified
        - Business context unclear
        - Success criteria undefined
        
        Args:
            analysis: Analysis dictionary from _analyse_request
            
        Returns:
            List of missing information items
        """
        self.logger.info("Detecting missing business information...")
        
        missing = []
        
        # Check for clear business objective
        if not analysis.get("business_objective") or analysis["business_objective"] == "Analyze":
            missing.append("Business objective not clearly specified")
        
        # Check for audience identification
        if not analysis.get("target_audience"):
            missing.append("Target audience not identified")
        
        # Check for business domain
        if not analysis.get("business_domain") or analysis["business_domain"] == "general":
            missing.append("Business domain not clearly specified")
        
        if missing:
            self.logger.warning(f"Missing business information: {missing}")
        else:
            self.logger.debug("No critical missing business information")
        
        return missing
    
    def _detect_conflicts(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Detect conflicting business requirements.
        
        Args:
            analysis: Analysis dictionary from _analyse_request
            
        Returns:
            List of detected conflicts
        """
        self.logger.info("Detecting requirement conflicts...")
        
        conflicts = []
        
        # Check for typical business-level conflicts
        text_lower = analysis["original_text"].lower()
        
        if ("real-time" in text_lower or "live" in text_lower) and \
           ("monthly" in text_lower or "annual" in text_lower):
            conflicts.append(
                "Conflicting expectations: Real-time data vs. monthly/annual reporting"
            )
        
        if ("executive" in text_lower or "ceo" in text_lower) and \
           ("detailed" in text_lower or "row-level" in text_lower):
            conflicts.append(
                "Potential conflict: Executive audience may not need row-level detail"
            )
        
        if len(conflicts) > 0:
            self.logger.warning(f"Conflicts detected: {conflicts}")
        else:
            self.logger.debug("No requirement conflicts detected")
        
        return conflicts
    
    def _detect_ambiguities(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Detect ambiguous wording in business requirement.
        
        Args:
            analysis: Analysis dictionary from _analyse_request
            
        Returns:
            List of detected ambiguities
        """
        self.logger.info("Detecting ambiguities...")
        
        ambiguities = []
        text = analysis["original_text"]
        text_lower = text.lower()
        
        # Check for vague quantifiers
        vague_terms = ["many", "few", "some", "several", "various", "all", "most"]
        found_vague = [term for term in vague_terms if f" {term} " in f" {text_lower} "]
        
        if found_vague:
            ambiguities.append(
                f"Vague quantifiers found: {', '.join(found_vague)}. Need specific scope."
            )
        
        # Check for undefined pronouns
        if " it " in f" {text_lower} " or " that " in f" {text_lower} ":
            ambiguities.append("Ambiguous pronouns (it, that). Unclear references.")
        
        # Check for unclear success criteria
        if "better" in text_lower or "improve" in text_lower or "good" in text_lower:
            ambiguities.append("Success criteria not clearly defined (what is 'better'?).")
        
        if len(ambiguities) > 0:
            self.logger.warning(f"Ambiguities detected: {ambiguities}")
        else:
            self.logger.debug("No significant ambiguities detected")
        
        return ambiguities
    
    def _normalize_business_terms(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize business terminology to standard terms.
        
        Design for LLM replacement: Can later call LLM for semantic equivalence.
        
        Args:
            analysis: Analysis dictionary from _analyse_request
            
        Returns:
            Normalized analysis dictionary
        """
        self.logger.info("Normalizing business terminology...")
        
        normalized = analysis.copy()
        
        # Normalize domain term
        if "domain" in normalized:
            domain = normalized.pop("domain")
            normalized["business_domain"] = self._normalize_term(domain)
        
        # Normalize objective
        if "objective" in normalized:
            obj = normalized.pop("objective")
            normalized["business_objective"] = self._normalize_term(obj)
        
        # Normalize audience
        if "audience" in normalized:
            aud = normalized.pop("audience")
            normalized["target_audience"] = [self._normalize_term(a) for a in aud]
        
        # Normalize grain
        if "grain" in normalized:
            grain = normalized.pop("grain")
            normalized["reporting_grain"] = self._normalize_term(grain)
        
        self.logger.debug(f"Normalized analysis: {normalized}")
        return normalized
    
    def _normalize_term(self, term: str) -> str:
        """
        Normalize a single term using standard mappings.
        
        Args:
            term: Term to normalize
            
        Returns:
            Normalized term
        """
        term_lower = term.lower().strip()
        
        # Check if term maps to a standard business term
        for category in BusinessTerminology:
            if term_lower in category.value:
                normalized = category.name.lower()
                self.logger.debug(f"Normalized '{term}' -> '{normalized}'")
                return normalized
        
        # If no mapping, return as-is
        self.logger.debug(f"No normalization found for '{term}'")
        return term_lower
    
    def _build_terminology_mappings(self) -> Dict[str, str]:
        """Build mappings for business terminology normalization."""
        mappings = {}
        for category in BusinessTerminology:
            for term in category.value:
                mappings[term.lower()] = category.name.lower()
        return mappings
    
    def _generate_assumptions(
        self, normalized: Dict[str, Any], missing_info: List[str]
    ) -> List[str]:
        """
        Generate safe assumptions when information is missing.
        
        Only generate assumptions for BUSINESS-level gaps.
        Do NOT assume technical details (measures, dimensions, schema).
        
        Args:
            normalized: Normalized analysis dictionary
            missing_info: List of missing information items
            
        Returns:
            List of assumptions
        """
        self.logger.info("Generating business assumptions...")
        
        assumptions = []
        
        # Assume time-based reporting if grain not specified
        if not normalized.get("reporting_grain") or normalized["reporting_grain"] == "general":
            assumptions.append(
                "Assuming time-based reporting aggregation (monthly or daily)"
            )
        
        # Assume internal audience if not specified
        if not normalized.get("target_audience") or normalized["target_audience"] == ["general"]:
            assumptions.append("Assuming dashboard is for internal business use")
        
        # Assume current time period filter if not specified
        if "business_domain" not in missing_info:
            assumptions.append("Assuming focus on recent/current time period data")
        
        # Log critical assumptions to require user confirmation
        if assumptions:
            self.logger.warning(
                f"Important assumptions generated (may need user confirmation): {assumptions}"
            )
        else:
            self.logger.debug("Minimal assumptions needed")
        
        return assumptions
    
    def _generate_follow_up_questions(
        self,
        normalized: Dict[str, Any],
        missing_info: List[str],
        ambiguities: List[str]
    ) -> List[str]:
        """
        Generate intelligent follow-up questions (business-level, not technical).
        
        Design for LLM replacement: Can later call LLM for natural conversation.
        
        Questions should feel like a Senior Business Analyst speaking with stakeholder.
        Limit questions to the minimum necessary.
        Ask about business intent and success, NOT about schema design.
        
        Args:
            normalized: Normalized analysis dictionary
            missing_info: List of missing information
            ambiguities: List of detected ambiguities
            
        Returns:
            List of follow-up questions (max 3)
        """
        self.logger.info("Generating business-focused follow-up questions...")
        
        questions = []
        
        # Priority 1: Clarify business objective if unclear
        if "business objective not clearly specified" in missing_info:
            questions.append(
                "What business problem are you trying to solve or what decision "
                "do you need to make with this dashboard?"
            )
        
        # Priority 2: Clarify audience if not identified
        if "Target audience not identified" in missing_info or not normalized.get("target_audience"):
            questions.append(
                "Who will use this dashboard? (e.g., sales managers, executives, analysts)"
            )
        
        # Priority 3: Clarify success criteria if ambiguous
        if any("success criteria" in amb.lower() for amb in ambiguities):
            questions.append(
                "How will you know if this dashboard is successful? "
                "What outcomes are you looking for?"
            )
        
        # Priority 4: Clarify time period if ambiguous
        if "reporting_grain" not in normalized or normalized["reporting_grain"] == "general":
            questions.append(
                "What time periods are most important for your analysis? "
                "(e.g., daily trends, monthly summaries)"
            )
        
        # Limit to maximum follow-up questions
        questions = questions[:MAX_FOLLOW_UP_QUESTIONS]
        
        self.logger.info(f"Generated {len(questions)} follow-up questions")
        return questions
    
    def _generate_conversation_summary(
        self,
        user_request: str,
        analysis: Dict[str, Any],
        assumptions: List[str] = []
    ) -> str:
        """
        Generate a concise summary of the clarified conversation.
        
        This summary becomes the primary business context for RequirementAgent.
        
        Example:
        "Original Request: 'I need a sales dashboard.'
        Conversation Summary: 'User requires a monthly sales dashboard for regional 
        managers showing revenue and profit by region for current fiscal year.'"
        
        Args:
            user_request: Original request
            analysis: Analysis results
            assumptions: List of assumptions made during clarification
            
        Returns:
            Conversation summary string
        """
        self.logger.info("Generating conversation summary...")
        
        summary = (
            f"The user wants to {analysis.get('business_intent', 'analyze').lower()} "
            f"a {analysis.get('business_domain', 'general')} dashboard. "
            f"The primary business objective is to {analysis.get('business_objective', 'analyze').lower()}. "
            f"The intended audience is {', '.join(analysis.get('target_audience', ['general users']))}. "
            f"The reporting grain is {analysis.get('reporting_grain', 'daily')}."
        )
        if assumptions:
            summary += ( f"The following assumptions were made during clarification: " + "; ".join(assumptions) + ".")
        
        self.logger.debug(f"Conversation summary: {summary}")
        return summary
    
    def _build_clarified_requirement(
        self,
        original_request: str,
        normalized: Dict[str, Any],
        assumptions: List[str],
        missing_info: List[str],
        ambiguities: List[str]
    ) -> ClarifiedRequirement:
        """
        Build the final ClarifiedRequirement object.
        
        NOTE: Does NOT include measures, dimensions, KPIs, filters, schema design.
        Those are RequirementAgent responsibilities.
        
        Args:
            original_request: Original user request
            normalized: Normalized analysis dictionary
            assumptions: Generated assumptions
            missing_info: Missing information items
            ambiguities: Detected ambiguities
            
        Returns:
            ClarifiedRequirement object
        """
        self.logger.info("Building clarified requirement...")
        
        # Build the clarified request statement
        clarified_request = (
            f"Business domain: {normalized.get('business_domain', 'general')}. "
            f"Objective: {normalized.get('business_objective', 'analyze')}. "
            f"Target audience: {', '.join(normalized.get('target_audience', ['general']))}. "
            f"Reporting grain: {normalized.get('reporting_grain', 'daily')}. "
            f"Key considerations: Missing information={', '.join(missing_info) if missing_info else 'none'}. "
            f"Ambiguities={', '.join(ambiguities) if ambiguities else 'none'}."
        )
        
        # Generate conversation summary for downstream agent
        conversation_summary = self._generate_conversation_summary(
            original_request, normalized, assumptions
        )
        
        requirement = ClarifiedRequirement(
            original_request=original_request,
            clarified_request=clarified_request,
            conversation_summary=conversation_summary,
            business_domain=normalized.get("business_domain", "general"),
            business_objective=normalized.get("business_objective", "analyze"),
            audience=normalized.get("target_audience", ["general"]),
            reporting_grain=normalized.get("reporting_grain", "daily"),
            assumptions=assumptions
        )
        
        self.logger.debug("Clarified requirement built successfully")
        return requirement
    
    def _calculate_confidence(
        self,
        missing_info: List[str],
        assumptions: List[str],
        ambiguities: List[str],
        conflicts: List[str]
    ) -> float:
        """
        Calculate confidence score based on modular factors.
        
        Confidence reflects how well we understand the business requirement.
        
        Scoring:
        - Start at 100%
        - Deduct for missing information (business-level)
        - Deduct for ambiguities
        - Deduct for conflicts
        - Deduct for unclarified assumptions
        
        Args:
            missing_info: List of missing information items
            assumptions: List of assumptions
            ambiguities: List of ambiguities
            conflicts: List of conflicts
            
        Returns:
            Confidence score (0-100)
        """
        self.logger.info("Calculating confidence score...")
        
        confidence = 100.0
        
        # Deduct for missing business information
        confidence -= len(missing_info) * MISSING_INFO_PENALTY
        
        # Deduct for ambiguities (these need clarification)
        confidence -= len(ambiguities) * AMBIGUITY_PENALTY
        
        # Deduct for conflicts (serious concern)
        confidence -= len(conflicts) * CONFLICT_PENALTY
        
        # Deduct for assumptions (but less than missing info)
        # Assumptions are acceptable as long as acknowledged
        confidence -= len(assumptions) * ASSUMPTION_PENALTY
        
        # Ensure confidence stays in valid range
        confidence = max(0, min(100, confidence))
        
        self.logger.info(f"Calculated confidence score: {confidence}%")
        return confidence
    
    def _determine_readiness(
        self,
        confidence: float,
        needs_input: bool,
        missing_info: List[str]
    ) -> Tuple[str, bool]:
        """
        Determine clarification status and readiness for downstream agent.
        
        Status flow:
        - pending: Initial state
        - needs_clarification: Waiting for user input
        - complete: Ready for RequirementAgent
        - error: Unable to clarify
        
        Args:
            confidence: Confidence score (0-100)
            needs_input: Whether follow-up questions were generated
            missing_info: List of missing information
            
        Returns:
            Tuple of (status, ready_for_downstream)
        """
        self.logger.info("Determining readiness...")
        
        if needs_input:
            status = "needs_clarification"
            ready = False
            self.logger.debug("Agent needs user input before proceeding")
        elif confidence >= READY_CONFIDENCE_THRESHOLD:
            status = ClarificationStatus.COMPLETE
            ready = True
            self.logger.debug("Clarification complete, ready for RequirementAgent")
        elif confidence >= NEEDS_CLARIFICATION_THRESHOLD:
            status = ClarificationStatus.NEEDS_CLARIFICATION
            ready = False
            self.logger.debug("Confidence acceptable but could benefit from clarification")
        else:
            status = ClarificationStatus.ERROR
            ready = False
            self.logger.warning(f"Confidence too low ({confidence}%). Unable to clarify.")
        
        return status, ready
    
    def _validate_output(self, clarified_req: ClarifiedRequirement) -> None:
        """
        Validate that clarified requirement meets basic quality standards.
        
        Args:
            clarified_req: The clarified requirement to validate
            
        Raises:
            ValueError: If validation fails
        """
        self.logger.info("Validating output...")
        
        # Check that required fields are populated
        if not clarified_req.business_objective or clarified_req.business_objective == "analyze":
            self.logger.warning("Business objective not clearly specified")
        
        if not clarified_req.conversation_summary:
            raise ValueError("Conversation summary is required")
        
        self.logger.debug("Output validation passed")
    
    def _build_result(
        self,
        clarified_req: ClarifiedRequirement,
        confidence: float,
        follow_up_questions: List[str],
        missing_info: List[str],
        ambiguities: List[str],
        assumptions: List[str],
        status: str,
        needs_input: bool,
        ready_for_downstream: bool
    ) -> ClarificationResult:
        """
        Build the final ClarificationResult object.
        
        Args:
            clarified_req: Clarified requirement
            confidence: Confidence score
            follow_up_questions: Questions to ask user
            missing_info: Missing information items
            ambiguities: Detected ambiguities
            assumptions: Generated assumptions
            status: Clarification status
            needs_input: Whether user input is needed
            ready_for_downstream: Whether ready for RequirementAgent
            
        Returns:
            ClarificationResult object
        """
        self.logger.info("Building clarification result...")
        
        # Validate output before building result
        self._validate_output(clarified_req)
        
        result = ClarificationResult(
            clarified_requirement=clarified_req,
            needs_user_input=needs_input,
            follow_up_questions=follow_up_questions,
            missing_information=missing_info,
            ambiguities_detected=ambiguities,
            confidence_score=confidence,
            conversation_history=[],
            ready_for_requirement_agent=ready_for_downstream,
            status=status,
            processing_timestamp=datetime.now()
        )
        
        self.logger.debug(
            f"Result: Status={status}, Confidence={confidence}%, "
            f"Needs input={needs_input}, Ready for downstream={ready_for_downstream}"
        )
        return result
