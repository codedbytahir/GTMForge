"""
GTMForge Base Agent
Custom base class for all GTMForge agents with shared infrastructure.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Type
from pydantic import BaseModel
import structlog
from datetime import datetime


class BaseAgent(ABC):
    """
    Abstract base class for all GTMForge agents.
    
    Provides:
    - Standardized agent metadata
    - Structured logging with agent context
    - Input/output validation via Pydantic
    - Async execution pattern
    - Timing and performance tracking
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        log_level: str = "INFO"
    ):
        """
        Initialize the base agent.
        
        Args:
            name: Agent name (e.g., "IdeationAgent")
            description: What this agent does
            version: Agent version for tracking
            log_level: Logging level
        """
        self.name = name
        self.description = description
        self.version = version
        self.logger = structlog.get_logger(agent_name=name, agent_version=version)
        self._execution_count = 0
        self._total_execution_time = 0.0
    
    @property
    @abstractmethod
    def input_schema(self) -> Type[BaseModel]:
        """
        Define the Pydantic model for input validation.
        Must be implemented by each agent.
        """
        pass
    
    @property
    @abstractmethod
    def output_schema(self) -> Type[BaseModel]:
        """
        Define the Pydantic model for output validation.
        Must be implemented by each agent.
        """
        pass
    
    @abstractmethod
    async def run(self, input_data: BaseModel) -> BaseModel:
        """
        Main execution method for the agent.
        Must be implemented by each agent.
        
        Args:
            input_data: Validated input matching input_schema
            
        Returns:
            Validated output matching output_schema
        """
        pass
    
    async def execute(self, input_data: dict | BaseModel) -> BaseModel:
        """
        Execute the agent with logging, validation, and timing.
        This wraps the run() method with common functionality.
        
        Args:
            input_data: Raw dict or Pydantic model to process
            
        Returns:
            Validated output from the agent
            
        Raises:
            ValidationError: If input/output validation fails
            Exception: Any errors during execution
        """
        start_time = datetime.now()
        self._execution_count += 1
        
        # Log agent start
        self.logger.info(
            "agent_started",
            execution_count=self._execution_count,
            input_type=type(input_data).__name__
        )
        
        try:
            # Validate input
            if isinstance(input_data, dict):
                validated_input = self.input_schema(**input_data)
            elif isinstance(input_data, BaseModel):
                validated_input = input_data
            else:
                raise ValueError(f"Invalid input type: {type(input_data)}")
            
            self.logger.debug("input_validated", schema=self.input_schema.__name__)
            
            # Execute the agent's logic
            output = await self.run(validated_input)
            
            # Validate output
            if not isinstance(output, self.output_schema):
                raise ValueError(
                    f"Agent returned wrong type. Expected {self.output_schema.__name__}, "
                    f"got {type(output).__name__}"
                )
            
            self.logger.debug("output_validated", schema=self.output_schema.__name__)
            
            # Log success
            execution_time = (datetime.now() - start_time).total_seconds()
            self._total_execution_time += execution_time
            
            self.logger.info(
                "agent_completed",
                execution_time_seconds=execution_time,
                avg_execution_time=self._total_execution_time / self._execution_count,
                success=True
            )
            
            return output
            
        except Exception as e:
            # Log failure
            execution_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.error(
                "agent_failed",
                execution_time_seconds=execution_time,
                error_type=type(e).__name__,
                error_message=str(e),
                success=False
            )
            raise
    
    def get_metadata(self) -> dict:
        """
        Get agent metadata for tracking and debugging.
        
        Returns:
            Dictionary with agent information
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "input_schema": self.input_schema.__name__,
            "output_schema": self.output_schema.__name__,
            "execution_count": self._execution_count,
            "total_execution_time": self._total_execution_time,
            "avg_execution_time": (
                self._total_execution_time / self._execution_count 
                if self._execution_count > 0 
                else 0
            )
        }
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"version='{self.version}', "
            f"executions={self._execution_count})"
        )