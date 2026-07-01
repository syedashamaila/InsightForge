import logging
import uuid
from datetime import datetime
from typing import Dict, Any

from agents.clarification_agent import ClarificationAgent
from agents.requirement_agent import RequirementAgent
from agents.mockdata_agent import MockDataAgent
from agents.prototype_agent import PrototypeAgent
from agents.reporter_agent import ReporterAgent


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class OrchestratorAgent:
    """
    Coordinates execution of all InsightForge agents.
    """

    def __init__(self):

        self.clarification_agent = ClarificationAgent()

        self.requirement_agent = RequirementAgent()

        self.prototype_agent = PrototypeAgent()

        self.reporter_agent = ReporterAgent()

        logger.info("OrchestratorAgent initialized.")

    def run_pipeline(
        self,
        business_requirement: str
    ) -> Dict[str, Any]:

        run_id = str(uuid.uuid4())

        start_time = datetime.utcnow()

        logger.info("Pipeline Started")

        try:

            ##################################################
            # STEP 1
            # Clarification Agent
            ##################################################

            clarification_result = self.clarification_agent.run(
                business_requirement
            )

            if clarification_result.needs_user_input:

                return {
                    "status": "Needs Clarification",
                    "run_id": run_id,
                    "clarification_result": clarification_result,
                    "generated_at": datetime.utcnow().isoformat()
                }

            ##################################################
            # STEP 2
            # Requirement Agent
            ##################################################

            requirement_result = self.requirement_agent.analyze_requirement(
                clarification_result.clarified_requirement
            )

            ##################################################
            # STEP 3
            # Mock Data Agent
            ##################################################

            mock_agent = MockDataAgent(
                requirement_result
            )

            mock_data_result = mock_agent.generate_mock_data()

            ##################################################
            # STEP 4
            # Prototype Agent
            ##################################################

            prototype_result = self.prototype_agent.create_prototype(
                requirement_result,
                clarification_result.to_dict(),
                mock_data_result
            )

            ##################################################
            # STEP 5
            # Reporter Agent
            ##################################################

            dashboard_result = self.reporter_agent.generate_dashboard(
                prototype_result,
                mock_data_result
            )

            execution_time = (
                datetime.utcnow() - start_time
            ).total_seconds()

            logger.info(
                "Pipeline completed in %.2f seconds",
                execution_time
            )

            return {

                "status": "Success",

                "run_id": run_id,

                "clarification_result":
                    clarification_result.to_dict(),

                "requirement_result":
                    requirement_result,

                "mock_data_result":
                    mock_data_result,

                "prototype_result":
                    prototype_result,

                "dashboard_result":
                    dashboard_result,

                "execution_time":
                    execution_time,

                "generated_at":
                    datetime.utcnow().isoformat()

            }

        except Exception as ex:

            logger.exception("Pipeline Failed")

            return {

                "status": "Failed",

                "run_id": run_id,

                "error": str(ex),

                "generated_at":
                    datetime.utcnow().isoformat()

            }
