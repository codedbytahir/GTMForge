"""
GTMForge Structured Logging Configuration
Configures structlog for consistent logging across all agents and components.
"""

import os
import sys
import structlog
from structlog.processors import JSONRenderer


def configure_logging(
    log_level: str = None,
    json_format: bool = None
) -> None:
    """
    Configure structlog for GTMForge.
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR). Defaults to env var or INFO
        json_format: Whether to use JSON output. Defaults to env var or based on APP_ENV
    """
    # Get configuration from environment if not provided
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    if json_format is None:
        app_env = os.getenv("APP_ENV", "development").lower()
        json_format = app_env == "production"
    
    # Configure processors
    processors = [
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.contextvars.merge_contextvars,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    # Add appropriate renderer based on environment
    if json_format:
        # Production: JSON format for log aggregation
        processors.append(JSONRenderer())
    else:
        # Development: Human-readable console output
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None, **initial_context) -> structlog.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (typically module or agent name)
        **initial_context: Initial context to bind to the logger
        
    Returns:
        Configured structlog logger
    """
    logger = structlog.get_logger(name)
    if initial_context:
        logger = logger.bind(**initial_context)
    return logger


# Initialize logging on module import
configure_logging()