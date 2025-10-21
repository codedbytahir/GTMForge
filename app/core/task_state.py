
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import structlog

logger = structlog.get_logger(__name__)


class TaskState:
    """
    In-memory task state manager for tracking pipeline execution.
    Stores task metadata, progress, and results.
    """
    
    def __init__(self):
        """Initialize empty task store."""
        self.tasks: Dict[str, Dict[str, Any]] = {}
        logger.info("task_state_manager_initialized")
    
    def create_task(self, task_id: str, input_data: Dict[str, Any]) -> None:
        """
        Create a new task with initial state.
        
        Args:
            task_id: Unique task identifier
            input_data: Input parameters (idea, industry, etc.)
        """
        self.tasks[task_id] = {
            "task_id": task_id,
            "status": "queued",
            "progress": 0.0,
            "current_stage": "initialization",
            "input_data": input_data,
            "result": None,
            "error": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "execution_time_seconds": None
        }
        
        logger.info(
            "task_created",
            task_id=task_id,
            status="queued",
            input_keys=list(input_data.keys())
        )
    
    def update_status(self, task_id: str, status: str, progress: float = None, current_stage: str = None) -> None:
        """
        Update task status and progress.
        
        Args:
            task_id: Task identifier
            status: New status (queued, running, completed, failed)
            progress: Progress percentage (0.0-100.0)
            current_stage: Current pipeline stage
        """
        if task_id not in self.tasks:
            logger.warning("task_not_found", task_id=task_id)
            return
        
        task = self.tasks[task_id]
        old_status = task["status"]
        
        # Update fields
        task["status"] = status
        task["updated_at"] = datetime.now().isoformat()
        
        if progress is not None:
            task["progress"] = max(0.0, min(100.0, progress))
        
        if current_stage is not None:
            task["current_stage"] = current_stage
        
        # Calculate execution time if completed
        if status in ["completed", "failed"]:
            created_at = datetime.fromisoformat(task["created_at"])
            execution_time = (datetime.now() - created_at).total_seconds()
            task["execution_time_seconds"] = execution_time
        
        logger.info(
            "task_status_updated",
            task_id=task_id,
            old_status=old_status,
            new_status=status,
            progress=task["progress"],
            current_stage=task["current_stage"]
        )
    
    def set_result(self, task_id: str, result: Dict[str, Any]) -> None:
        """
        Set task result data.
        
        Args:
            task_id: Task identifier
            result: Result data (manifest, qa_report, etc.)
        """
        if task_id not in self.tasks:
            logger.warning("task_not_found", task_id=task_id)
            return
        
        self.tasks[task_id]["result"] = result
        self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
        
        logger.info(
            "task_result_set",
            task_id=task_id,
            result_keys=list(result.keys()) if result else []
        )
    
    def set_error(self, task_id: str, error: str) -> None:
        """
        Set task error.
        
        Args:
            task_id: Task identifier
            error: Error message
        """
        if task_id not in self.tasks:
            logger.warning("task_not_found", task_id=task_id)
            return
        
        self.tasks[task_id]["error"] = error
        self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
        
        logger.error(
            "task_error_set",
            task_id=task_id,
            error=error
        )
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task data.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task data dictionary or None if not found
        """
        task = self.tasks.get(task_id)
        
        if task:
            logger.debug("task_retrieved", task_id=task_id, status=task["status"])
        else:
            logger.warning("task_not_found", task_id=task_id)
        
        return task
    
    def list_tasks(self, status_filter: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        List all tasks, optionally filtered by status.
        
        Args:
            status_filter: Optional status to filter by
            
        Returns:
            Dictionary of task_id -> task_data
        """
        if status_filter:
            filtered_tasks = {
                task_id: task_data 
                for task_id, task_data in self.tasks.items()
                if task_data["status"] == status_filter
            }
            logger.info("tasks_listed", count=len(filtered_tasks), status_filter=status_filter)
            return filtered_tasks
        else:
            logger.info("tasks_listed", count=len(self.tasks))
            return self.tasks.copy()
    
    def cleanup_old_tasks(self, max_age_hours: int = 24) -> int:
        """
        Clean up old completed/failed tasks.
        
        Args:
            max_age_hours: Maximum age in hours for tasks to keep
            
        Returns:
            Number of tasks cleaned up
        """
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        tasks_to_remove = []
        
        for task_id, task_data in self.tasks.items():
            if task_data["status"] in ["completed", "failed"]:
                created_at = datetime.fromisoformat(task_data["created_at"]).timestamp()
                if created_at < cutoff_time:
                    tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
        
        logger.info(
            "old_tasks_cleaned",
            removed_count=len(tasks_to_remove),
            max_age_hours=max_age_hours
        )
        
        return len(tasks_to_remove)


task_state = TaskState()


def generate_task_id() -> str:
    """Generate a unique task ID."""
    return f"task_{uuid.uuid4().hex[:12]}"
