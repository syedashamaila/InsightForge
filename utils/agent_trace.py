"""
Agent Trace Module

This module provides a reusable AgentTrace class for tracking and recording
execution information for agents in a multi-agent system. It maintains a
centralized trace of agent activities including execution status, timing,
inputs, outputs, and error information.

Author: AgenticAI System
Version: 1.0.0
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Enumeration for agent execution status."""

    STARTED = "Started"
    SUCCESS = "Success"
    FAILED = "Failed"


@dataclass
class TraceRecord:
    """Data class representing a single agent execution trace record."""

    agent_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    execution_duration: Optional[float] = None
    status: ExecutionStatus = ExecutionStatus.STARTED
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert trace record to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the trace record.
        """
        data = asdict(self)
        data['status'] = self.status.value
        data['start_time'] = self.start_time.isoformat()
        if data['end_time']:
            data['end_time'] = data['end_time'].isoformat()
        return data


class AgentTrace:
    """
    A production-ready trace manager for recording and tracking agent
    execution information in a multi-agent system.

    This class maintains a centralized registry of all agent activities,
    including execution timing, status, inputs, outputs, and errors.
    It is designed to be generic and reusable across all agent types
    in the system without any business-specific logic.

    Attributes:
        _traces (List[TraceRecord]): In-memory list of trace records.
        _active_traces (Dict[str, TraceRecord]): Dictionary of active traces
            keyed by agent_name.
    """

    def __init__(self) -> None:
        """Initialize the AgentTrace instance."""
        self._traces: List[TraceRecord] = []
        self._active_traces: Dict[str, TraceRecord] = {}
        logger.info("AgentTrace initialized")

    def start_trace(
        self,
        agent_name: str,
        input_summary: Optional[str] = None
    ) -> TraceRecord:
        """
        Start tracing execution for an agent.

        This method creates a new trace record and marks the start time.
        If a trace for the agent already exists, it will be replaced.

        Args:
            agent_name (str): The name of the agent starting execution.
            input_summary (Optional[str]): A summary of the input provided
                to the agent. Defaults to None.

        Returns:
            TraceRecord: The created trace record.

        Raises:
            ValueError: If agent_name is empty or None.
        """
        if not agent_name or not isinstance(agent_name, str):
            error_msg = "agent_name must be a non-empty string"
            logger.error(error_msg)
            raise ValueError(error_msg)

        trace_record = TraceRecord(
            agent_name=agent_name,
            start_time=datetime.now(),
            input_summary=input_summary,
            status=ExecutionStatus.STARTED
        )

        self._active_traces[agent_name] = trace_record
        logger.info(
            f"Started trace for agent '{agent_name}' "
            f"with input: {input_summary}"
        )

        return trace_record

    def end_trace(
        self,
        agent_name: str,
        output_summary: Optional[str] = None
    ) -> Optional[TraceRecord]:
        """
        End tracing execution for an agent and mark it as successful.

        This method marks the end time, calculates execution duration,
        and updates the status to SUCCESS. The trace is moved from active
        to the permanent traces list.

        Args:
            agent_name (str): The name of the agent ending execution.
            output_summary (Optional[str]): A summary of the output produced
                by the agent. Defaults to None.

        Returns:
            Optional[TraceRecord]: The completed trace record, or None if
                no active trace found for the agent.

        Raises:
            ValueError: If agent_name is empty or None.
        """
        if not agent_name or not isinstance(agent_name, str):
            error_msg = "agent_name must be a non-empty string"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if agent_name not in self._active_traces:
            logger.warning(
                f"No active trace found for agent '{agent_name}'"
            )
            return None

        trace_record = self._active_traces[agent_name]
        trace_record.end_time = datetime.now()
        trace_record.execution_duration = (
            trace_record.end_time - trace_record.start_time
        ).total_seconds()
        trace_record.status = ExecutionStatus.SUCCESS
        trace_record.output_summary = output_summary

        self._traces.append(trace_record)
        del self._active_traces[agent_name]

        logger.info(
            f"Successfully ended trace for agent '{agent_name}' "
            f"with output: {output_summary} "
            f"(duration: {trace_record.execution_duration:.2f}s)"
        )

        return trace_record

    def fail_trace(
        self,
        agent_name: str,
        error_message: Optional[str] = None,
        output_summary: Optional[str] = None
    ) -> Optional[TraceRecord]:
        """
        End tracing execution for an agent and mark it as failed.

        This method marks the end time, calculates execution duration,
        updates the status to FAILED, and records the error message.
        The trace is moved from active to the permanent traces list.

        Args:
            agent_name (str): The name of the agent that failed.
            error_message (Optional[str]): A description of the error that
                occurred. Defaults to None.
            output_summary (Optional[str]): A summary of the partial output
                before failure. Defaults to None.

        Returns:
            Optional[TraceRecord]: The failed trace record, or None if
                no active trace found for the agent.

        Raises:
            ValueError: If agent_name is empty or None.
        """
        if not agent_name or not isinstance(agent_name, str):
            error_msg = "agent_name must be a non-empty string"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if agent_name not in self._active_traces:
            logger.warning(
                f"No active trace found for agent '{agent_name}'"
            )
            return None

        trace_record = self._active_traces[agent_name]
        trace_record.end_time = datetime.now()
        trace_record.execution_duration = (
            trace_record.end_time - trace_record.start_time
        ).total_seconds()
        trace_record.status = ExecutionStatus.FAILED
        trace_record.error_message = error_message
        trace_record.output_summary = output_summary

        self._traces.append(trace_record)
        del self._active_traces[agent_name]

        logger.error(
            f"Failed trace for agent '{agent_name}' "
            f"with error: {error_message} "
            f"(duration: {trace_record.execution_duration:.2f}s)"
        )

        return trace_record

    def get_all_traces(self) -> List[Dict[str, Any]]:
        """
        Retrieve all completed trace records.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing
                all completed trace records.
        """
        traces_list = [trace.to_dict() for trace in self._traces]
        logger.info(f"Retrieved {len(traces_list)} trace records")
        return traces_list

    def get_traces_by_agent(self, agent_name: str) -> List[Dict[str, Any]]:
        """
        Retrieve all trace records for a specific agent.

        Args:
            agent_name (str): The name of the agent to filter traces by.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing
                trace records for the specified agent.

        Raises:
            ValueError: If agent_name is empty or None.
        """
        if not agent_name or not isinstance(agent_name, str):
            error_msg = "agent_name must be a non-empty string"
            logger.error(error_msg)
            raise ValueError(error_msg)

        filtered_traces = [
            trace.to_dict()
            for trace in self._traces
            if trace.agent_name == agent_name
        ]
        logger.info(
            f"Retrieved {len(filtered_traces)} trace records for "
            f"agent '{agent_name}'"
        )
        return filtered_traces

    def get_traces_by_status(
        self,
        status: ExecutionStatus
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all trace records with a specific execution status.

        Args:
            status (ExecutionStatus): The execution status to filter by.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing
                trace records with the specified status.
        """
        filtered_traces = [
            trace.to_dict()
            for trace in self._traces
            if trace.status == status
        ]
        logger.info(
            f"Retrieved {len(filtered_traces)} trace records with "
            f"status '{status.value}'"
        )
        return filtered_traces

    def clear_traces(self) -> None:
        """
        Clear all trace records from memory.

        This method removes all completed traces from the internal list.
        Active traces are not affected by this operation.

        Warning:
            This operation is irreversible. All trace data will be lost.
        """
        count = len(self._traces)
        self._traces.clear()
        logger.warning(
            f"Cleared {count} trace records from memory"
        )

    def get_trace_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all traces including statistics.

        Returns:
            Dict[str, Any]: A dictionary containing trace statistics
                including total traces, successful traces, failed traces,
                and average execution duration.
        """
        total_traces = len(self._traces)
        successful = len([
            t for t in self._traces
            if t.status == ExecutionStatus.SUCCESS
        ])
        failed = len([
            t for t in self._traces
            if t.status == ExecutionStatus.FAILED
        ])

        avg_duration = 0.0
        if total_traces > 0:
            total_duration = sum(
                t.execution_duration or 0 for t in self._traces
            )
            avg_duration = total_duration / total_traces

        summary = {
            "total_traces": total_traces,
            "successful_traces": successful,
            "failed_traces": failed,
            "average_duration_seconds": round(avg_duration, 2),
            "active_traces": len(self._active_traces)
        }

        logger.info(f"Trace summary: {summary}")
        return summary
