"""
GTMForge Structured Logging Configuration
Configures structlog for consistent logging across all agents and components.
Phase 3: Adds per-task log files to /logs folder.
"""

import os
import sys
import logging
import structlog
from structlog.processors import JSONRenderer
from pathlib import Path


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


def setup_task_logging(task_id: str) -> structlog.BoundLogger:
    """
    Setup per-task logging to /logs/task_{task_id}.log file.
    
    Args:
        task_id: Unique task identifier
        
    Returns:
        Logger bound to task context
    """
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create task-specific log file
    log_file = logs_dir / f"task_{task_id}.log"
    
    # Create file handler
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Create formatter for file logs
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Create task logger
    task_logger = logging.getLogger(f"task_{task_id}")
    task_logger.setLevel(logging.DEBUG)
    task_logger.addHandler(file_handler)
    
    # Prevent duplicate logs
    task_logger.propagate = False
    
    # Create structlog logger bound to task
    bound_logger = structlog.get_logger(f"task_{task_id}")
    bound_logger = bound_logger.bind(task_id=task_id)
    
    return bound_logger


def cleanup_task_logs(max_age_hours: int = 24) -> int:
    """
    Clean up old task log files.
    
    Args:
        max_age_hours: Maximum age in hours for log files to keep
        
    Returns:
        Number of log files cleaned up
    """
    import time
    from datetime import datetime, timedelta
    
    logs_dir = Path("logs")
    if not logs_dir.exists():
        return 0
    
    cutoff_time = time.time() - (max_age_hours * 3600)
    cleaned_count = 0
    
    for log_file in logs_dir.glob("task_*.log"):
        if log_file.stat().st_mtime < cutoff_time:
            log_file.unlink()
            cleaned_count += 1
    
    return cleaned_count


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