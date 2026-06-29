"""
Multi-Agent BI Requirement Analysis System - Orchestrator Agent.

This module coordinates the sequential execution of four agents:
1. RequirementAgent - Analyzes business requirements
2. ClarificationAgent - Clarifies and refines requirements
3. PrototypeAgent - Creates prototypes based on clarified requirements
4. ReporterAgent - Generates final report

The orchestrator manages the workflow, traces execution, and handles errors.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any

from agents.requirement_agent import RequirementAgent
from agents.clarification_agent import ClarificationAgent
from agents.prototype_agent import PrototypeAgent
from agents.reporter_agent import ReporterAgent

from utils.agent_trace import AgentTrace
from utils.agent_factory import AgentFactory


class OrchestratorAgent:
    """Orchestrates the Multi-Agent BI Requirement Analysis workflow.

    This class coordinates the execution of four sequential agents to process
    business requirements through analysis, clarification, prototyping, and
    reporting stages. It manages tracing, logging, and error handling for the
    entire pipeline.

    Attributes:
        logger (logging.Logger): Logger instance for operation tracking.
        agent_trace (AgentTrace): Execution trace collector for the pipeline.
        agent_factory (AgentFactory): Factory for creating/retrieving agents.
        requirement_agent (RequirementAgent): Agent for requirement analysis.
        clarification_agent (ClarificationAgent): Agent for requirement clarification.
        prototype_agent (PrototypeAgent): Agent for prototype creation.
        reporter_agent (ReporterAgent): Agent for report generation.
    """

    def __init__(self) -> None:

        """Initialize the OrchestratorAgent with logger, trace, and agents.

        Sets up logging, creates an execution trace collector, initializes the
        agent factory, and retrieves or creates all four required agents.
        """
        self.logger = self._setup_logger()
        self.agent_trace = AgentTrace()
        self.agent_factory = AgentFactory()

        self.requirement_agent: RequirementAgent = self.agent_factory.get_agent(
            "RequirementAgent"
        )
        self.clarification_agent: ClarificationAgent = self.agent_factory.get_agent(
            "ClarificationAgent"
        )
        self.prototype_agent: PrototypeAgent = self.agent_factory.get_agent(
            "PrototypeAgent"
        )
        self.reporter_agent: ReporterAgent = self.agent_factory.get_agent(
            "ReporterAgent"
        )
        self.logger.info("OrchestratorAgent initialized with all agents")

    @staticmethod
    def _setup_logger() -> logging.Logger:
        """Set up and return a logger instance.

        Returns:
            logging.Logger: Configured logger for the orchestrator.
        """
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def run_pipeline(
        self, business_requirement: str, business_context: str = ""
    ) -> Dict[str, Any]:
        """Execute the complete BI requirement analysis pipeline.

        Orchestrates sequential execution of requirement analysis, clarification,
        prototyping, and reporting agents. Manages workflow state, traces execution,
        and handles errors gracefully.

        Args:
            business_requirement (str): The primary business requirement to analyze.
            business_context (str, optional): Additional context for the requirement.
                Defaults to "".

        Returns:
            Dict[str, Any]: Pipeline execution result containing:
                - run_id: Unique pipeline execution identifier
                - status: "Success" or "Failed"
                - requirement_result: Output from RequirementAgent
                - clarification_result: Output from ClarificationAgent
                - prototype_result: Output from PrototypeAgent
                - report_path: Path to generated report (if successful)
                - generated_at: ISO format timestamp
                - failed_agent: Agent name if failed (only on error)
                - error: Error message (only on failure)
        """
        run_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        try:
            # Step 1: Start pipeline execution trace
            self.logger.info("Pipeline Started")
            self.agent_trace.start_pipeline(run_id)

            # Step 2: Execute RequirementAgent
            requirement_result = self._execute_requirement_agent(
                run_id, business_requirement, business_context
            )

            # Step 3: Execute ClarificationAgent
            clarification_result = self._execute_clarification_agent(
                run_id, requirement_result
            )

            # Step 4: Execute PrototypeAgent
            prototype_result = self._execute_prototype_agent(
                run_id, requirement_result, clarification_result
            )

            # Step 5: Execute ReporterAgent
            report_result = self._execute_reporter_agent(
                run_id, requirement_result, clarification_result, prototype_result
            )

            # Step 6: Record pipeline completion
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.agent_trace.complete_pipeline(run_id, execution_time)
            self.logger.info("Pipeline Finished")

            return {
                "run_id": run_id,
                "status": "Success",
                "requirement_result": requirement_result,
                "clarification_result": clarification_result,
                "prototype_result": prototype_result,
                "report_result": report_result,
                "report_path": report_result.get("report_path"),
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as exc:
            self.logger.exception("Pipeline execution failed")
            self.agent_trace.fail_trace("Pipeline", str(exc))

            return {
                "run_id": run_id,
                "status": "Failed",
                "failed_agent": self._extract_failed_agent(str(exc)),
                "error": str(exc),
                "generated_at": datetime.utcnow().isoformat(),
            }

    def _execute_requirement_agent(
        self, run_id: str, business_requirement: str, business_context: str
    ) -> Dict[str, Any]:
        """Execute the RequirementAgent step.

        Args:
            run_id (str): Unique pipeline run identifier.
            business_requirement (str): The business requirement to analyze.
            business_context (str): Additional context for analysis.

        Returns:
            Dict[str, Any]: Analysis result from RequirementAgent.

        Raises:
            Exception: If agent execution fails.
        """
        self.agent_trace.start_agent("RequirementAgent", run_id)
        try:
            result = self.requirement_agent.analyze(
                business_requirement, business_context
            )
            self.agent_trace.complete_agent("RequirementAgent")
            self.logger.info("Requirement Agent Completed")
            return result
        except Exception as exc:
            self.agent_trace.complete_agent("RequirementAgent", error=str(exc))
            raise

    def _execute_clarification_agent(
        self, run_id: str, requirement_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the ClarificationAgent step.

        Args:
            run_id (str): Unique pipeline run identifier.
            requirement_result (Dict[str, Any]): Output from RequirementAgent.

        Returns:
            Dict[str, Any]: Clarification result from ClarificationAgent.

        Raises:
            Exception: If agent execution fails.
        """
        self.agent_trace.start_agent("ClarificationAgent", run_id)
        try:
            result = self.clarification_agent.clarify(requirement_result)
            self.agent_trace.complete_agent("ClarificationAgent")
            self.logger.info("Clarification Agent Completed")
            return result
        except Exception as exc:
            self.agent_trace.complete_agent("ClarificationAgent", error=str(exc))
            raise

    def _execute_prototype_agent(
        self,
        run_id: str,
        requirement_result: Dict[str, Any],
        clarification_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute the PrototypeAgent step.

        Args:
            run_id (str): Unique pipeline run identifier.
            requirement_result (Dict[str, Any]): Output from RequirementAgent.
            clarification_result (Dict[str, Any]): Output from ClarificationAgent.

        Returns:
            Dict[str, Any]: Prototype result from PrototypeAgent.

        Raises:
            Exception: If agent execution fails.
        """
        self.agent_trace.start_agent("PrototypeAgent", run_id)
        try:
            result = self.prototype_agent.create_prototype(
                requirement_result, clarification_result
            )
            self.agent_trace.complete_agent("PrototypeAgent")
            self.logger.info("Prototype Agent Completed")
            return result
        except Exception as exc:
            self.agent_trace.complete_agent("PrototypeAgent", error=str(exc))
            raise

    def _execute_reporter_agent(
        self,
        run_id: str,
        requirement_result: Dict[str, Any],
        clarification_result: Dict[str, Any],
        prototype_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute the ReporterAgent step.

        Args:
            run_id (str): Unique pipeline run identifier.
            requirement_result (Dict[str, Any]): Output from RequirementAgent.
            clarification_result (Dict[str, Any]): Output from ClarificationAgent.
            prototype_result (Dict[str, Any]): Output from PrototypeAgent.

        Returns:
            str: Path to generated report.

        Raises:
            Exception: If agent execution fails.
        """
        self.agent_trace.start_agent("ReporterAgent", run_id)
        try:
            report_result = self.reporter_agent.generate_report(
                requirement_result, clarification_result, prototype_result, run_id
            )
            self.agent_trace.complete_agent("ReporterAgent")
            self.logger.info("Reporter Agent Completed")
            return report_result
        
        except Exception as exc:
            self.agent_trace.complete_agent("ReporterAgent", error=str(exc))
            raise

    @staticmethod
    def _extract_failed_agent(error_message: str) -> str:
        """Extract failed agent name from error message.

        Args:
            error_message (str): Error message from pipeline execution.

        Returns:
            str: Name of the failed agent or "Unknown".
        """
        agent_names = [
            "RequirementAgent",
            "ClarificationAgent",
            "PrototypeAgent",
            "ReporterAgent",
        ]
        for agent_name in agent_names:
            if agent_name in error_message:
                return agent_name
        return "Unknown"
