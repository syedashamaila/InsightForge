"""Agent Factory Module for Multi-Agent Requirement Analysis System.

This module provides a factory pattern implementation for creating and managing
agent instances in a multi-agent system. It supports lazy initialization,
dynamic agent registration, and extensibility without modifying existing code.
"""

import logging
from typing import Any, Dict, Optional, Type

# Configure logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AgentFactory:
    """Factory for creating and managing agent instances.

    This class implements the factory pattern to create, store, and manage
    agent instances with lazy initialization. It supports dynamic registration
    of agent types and provides methods for agent lifecycle management.

    Attributes:
        _agents (Dict[str, Any]): Internal dictionary storing instantiated agents.
        _agent_classes (Dict[str, Type]): Registry of available agent classes.
        _instance (Optional[AgentFactory]): Singleton instance of the factory.
    """

    _instance: Optional['AgentFactory'] = None
    _agents: Dict[str, Any] = {}
    _agent_classes: Dict[str, Type] = {}

    def __new__(cls) -> 'AgentFactory':
        """Create or return singleton instance of AgentFactory.

        Returns:
            AgentFactory: The singleton instance of the factory.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            from agents.requirement_agent import RequirementAgent
            from agents.clarification_agent import ClarificationAgent
            from agents.prototype_agent import PrototypeAgent
            from agents.reporter_agent import ReporterAgent

            cls._instance.register_agent("RequirementAgent", RequirementAgent)
            cls._instance.register_agent("ClarificationAgent", ClarificationAgent)
            cls._instance.register_agent("PrototypeAgent", PrototypeAgent)
            cls._instance.register_agent("ReporterAgent", ReporterAgent)
            
            logger.debug('AgentFactory singleton instance created')
        return cls._instance

    def register_agent(self, agent_name: str, agent_class: Type) -> None:
        """Register an agent class in the factory.

        This method registers a new agent class that can be instantiated
        later via get_agent(). The same agent can be registered multiple times
        to update its class definition.

        Args:
            agent_name (str): The name identifier for the agent.
            agent_class (Type): The class/type to instantiate for this agent.

        Raises:
            ValueError: If agent_name is empty or agent_class is not a class.

        Example:
            >>> factory.register_agent('custom_agent', CustomAgentClass)
        """
        if not agent_name or not isinstance(agent_name, str):
            logger.error('Invalid agent_name: must be non-empty string')
            raise ValueError('agent_name must be a non-empty string')

        if not isinstance(agent_class, type):
            logger.error(
                'Invalid agent_class for %s: must be a class',
                agent_name
            )
            raise ValueError('agent_class must be a class type')

        self._agent_classes[agent_name] = agent_class
        # Reset cached instance to allow re-registration
        if agent_name in self._agents:
            del self._agents[agent_name]
            logger.debug(
                'Cleared cached instance for agent: %s',
                agent_name
            )
        logger.info('Agent registered: %s', agent_name)

    def get_agent(self, agent_name: str) -> Any:
        """Get or create an agent instance.

        Retrieves an agent instance by name. If the agent hasn't been
        instantiated yet, it is created and cached for future use (lazy
        initialization). Subsequent calls return the cached instance.

        Args:
            agent_name (str): The name identifier of the agent to retrieve.

        Returns:
            Any: An instance of the requested agent.

        Raises:
            ValueError: If the agent_name is not registered or empty.

        Example:
            >>> requirement_agent = factory.get_agent('requirement_agent')
        """
        if not agent_name or not isinstance(agent_name, str):
            logger.error('Invalid agent_name: must be non-empty string')
            raise ValueError('agent_name must be a non-empty string')

        # Return cached agent if available
        if agent_name in self._agents:
            logger.debug('Returning cached agent: %s', agent_name)
            return self._agents[agent_name]

        # Check if agent class is registered
        if agent_name not in self._agent_classes:
            logger.error('Unknown agent requested: %s', agent_name)
            raise ValueError(f'Unknown agent: {agent_name}')

        # Create and cache new instance
        agent_class = self._agent_classes[agent_name]
        try:
            agent_instance = agent_class()
            self._agents[agent_name] = agent_instance
            logger.info('Agent created and cached: %s', agent_name)
            return agent_instance
        except Exception as exc:
            logger.error(
                'Failed to instantiate agent %s: %s',
                agent_name,
                str(exc)
            )
            raise

    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """List all registered and instantiated agents.

        Returns a dictionary containing information about all registered
        agents, including their registration status and instantiation status.

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary with agent information.
                Keys are agent names, values are dicts with 'registered' and
                'instantiated' status flags.

        Example:
            >>> agents = factory.list_agents()
            >>> for name, info in agents.items():
            ...     print(f'{name}: {info}')
        """
        agents_info = {}
        all_agent_names = set(self._agent_classes.keys()) | set(
            self._agents.keys()
        )

        for agent_name in all_agent_names:
            agents_info[agent_name] = {
                'registered': agent_name in self._agent_classes,
                'instantiated': agent_name in self._agents,
            }

        logger.debug('Listed agents: %d total', len(agents_info))
        return agents_info

    def clear_agents(self) -> None:
        """Clear all cached agent instances.

        Removes all instantiated agent instances from the cache. Registered
        agent classes remain intact and can be instantiated again.
        Does not affect agent registrations.

        Example:
            >>> factory.clear_agents()
        """
        cleared_count = len(self._agents)
        self._agents.clear()
        logger.info('Cleared %d cached agent instances', cleared_count)

    def unregister_agent(self, agent_name: str) -> None:
        """Unregister an agent class from the factory.

        Removes an agent class from the registry and clears its cached
        instance if present.

        Args:
            agent_name (str): The name identifier of the agent to unregister.

        Raises:
            ValueError: If agent_name is not registered.

        Example:
            >>> factory.unregister_agent('custom_agent')
        """
        if agent_name not in self._agent_classes:
            logger.error('Cannot unregister unknown agent: %s', agent_name)
            raise ValueError(f'Agent not registered: {agent_name}')

        del self._agent_classes[agent_name]
        if agent_name in self._agents:
            del self._agents[agent_name]
        logger.info('Agent unregistered: %s', agent_name)

    def get_agent_info(self, agent_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific agent.

        Returns metadata about a registered agent including its class
        and instantiation status.

        Args:
            agent_name (str): The name identifier of the agent.

        Returns:
            Dict[str, Any]: Dictionary with agent class and status information.

        Raises:
            ValueError: If agent_name is not registered.

        Example:
            >>> info = factory.get_agent_info('requirement_agent')
        """
        if agent_name not in self._agent_classes:
            logger.error('Agent not found: %s', agent_name)
            raise ValueError(f'Agent not registered: {agent_name}')

        return {
            'name': agent_name,
            'class': self._agent_classes[agent_name],
            'instantiated': agent_name in self._agents,
        }

    @classmethod
    def reset_singleton(cls) -> None:
        """Reset the singleton instance and clear all agents.

        This method should be used with caution, primarily for testing.
        It clears all cached agents and the singleton instance.

        Example:
            >>> AgentFactory.reset_singleton()
        """
        cls._agents.clear()
        cls._agent_classes.clear()
        cls._instance = None
        logger.debug('AgentFactory singleton reset')
