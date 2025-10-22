"""
GTMForge FastAPI Backend - Phase 3
REST and WebSocket API for GTMForge pipeline execution.
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

from app.core.task_state import task_state, generate_task_id
from app.core.orchestrator import GTMForgeOrchestrator
from app.utils.logger import setup_task_logging, cleanup_task_logs


# Pydantic models for API
class GenerateIdeaRequest(BaseModel):
    idea: str = Field(..., description="Business idea to generate assets for")
    industry: str = Field(..., description="Industry context for the idea")


class GenerateIdeaResponse(BaseModel):
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Initial task status")
    message: str = Field(..., description="Status message")


class TaskStatusResponse(BaseModel):
    task_id: str = Field(..., description="Task identifier")
    status: str = Field(..., description="Current task status")
    progress: float = Field(..., description="Progress percentage (0-100)")
    current_stage: str = Field(..., description="Current pipeline stage")
    created_at: str = Field(..., description="Task creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class TaskResultsResponse(BaseModel):
    task_id: str = Field(..., description="Task identifier")
    status: str = Field(..., description="Final task status")
    manifest: Optional[Dict[str, Any]] = Field(None, description="Published manifest")
    qa_report: Optional[Dict[str, Any]] = Field(None, description="QA validation report")
    execution_time_seconds: Optional[float] = Field(None, description="Total execution time")
    error: Optional[str] = Field(None, description="Error message if failed")


# Initialize FastAPI app
app = FastAPI(
    title="GTMForge API",
    description="AI-powered pitch deck generation with Imagen, Veo, and Canva",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving local assets
from app.utils.config import OUTPUT_DIR
app.mount("/assets", StaticFiles(directory=str(OUTPUT_DIR / "assets")), name="assets")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, task_id: str):
        await websocket.accept()
        self.active_connections[task_id] = websocket

    def disconnect(self, task_id: str):
        if task_id in self.active_connections:
            del self.active_connections[task_id]

    async def send_to_task(self, task_id: str, message: Dict[str, Any]):
        if task_id in self.active_connections:
            try:
                await self.active_connections[task_id].send_text(json.dumps(message))
            except:
                # Connection closed, remove it
                self.disconnect(task_id)

manager = ConnectionManager()


@app.post("/generate_idea", response_model=GenerateIdeaResponse)
async def generate_idea(request: GenerateIdeaRequest):
    """
    Start a new GTMForge pipeline for the given business idea.
    
    Returns immediately with task_id for status polling.
    """
    # Generate unique task ID
    task_id = generate_task_id()
    
    # Create task in state manager
    input_data = {
        "idea": request.idea,
        "industry": request.industry,
        "created_at": datetime.now().isoformat()
    }
    task_state.create_task(task_id, input_data)
    
    # Start background orchestrator execution
    asyncio.create_task(run_orchestrator_background(task_id, request.idea, request.industry))
    
    return GenerateIdeaResponse(
        task_id=task_id,
        status="queued",
        message="Pipeline started successfully"
    )


@app.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get current status and progress of a task.
    """
    task = task_state.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        current_stage=task["current_stage"],
        created_at=task["created_at"],
        updated_at=task["updated_at"]
    )


@app.get("/results/{task_id}", response_model=TaskResultsResponse)
async def get_task_results(task_id: str):
    """
    Get final results of a completed task.
    """
    task = task_state.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task["status"] not in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Task not completed yet")
    
    response = TaskResultsResponse(
        task_id=task_id,
        status=task["status"],
        execution_time_seconds=task.get("execution_time_seconds")
    )
    
    if task["status"] == "completed" and task.get("result"):
        result = task["result"]
        response.manifest = result.get("manifest")
        response.qa_report = result.get("qa_report")
    elif task["status"] == "failed":
        response.error = task.get("error", "Unknown error")
    
    return response


@app.websocket("/ws/progress/{task_id}")
async def websocket_progress(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for real-time progress updates.
    """
    await manager.connect(websocket, task_id)
    
    try:
        # Send initial status
        task = task_state.get_task(task_id)
        if task:
            await websocket.send_text(json.dumps({
                "type": "status",
                "task_id": task_id,
                "status": task["status"],
                "progress": task["progress"],
                "current_stage": task["current_stage"],
                "timestamp": datetime.now().isoformat()
            }))
        
        # Keep connection alive and send updates
        while True:
            # Check for task updates
            task = task_state.get_task(task_id)
            if task and task["status"] in ["completed", "failed"]:
                # Send final status and close
                await websocket.send_text(json.dumps({
                    "type": "final",
                    "task_id": task_id,
                    "status": task["status"],
                    "progress": 100.0 if task["status"] == "completed" else task["progress"],
                    "result": task.get("result"),
                    "error": task.get("error"),
                    "timestamp": datetime.now().isoformat()
                }))
                break
            
            # Wait before next check
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        manager.disconnect(task_id)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_tasks": len(task_state.list_tasks())
    }


@app.get("/tasks")
async def list_tasks():
    """
    List all tasks (for debugging).
    """
    return task_state.list_tasks()


async def run_orchestrator_background(task_id: str, idea: str, industry: str):
    """
    Background task to run the orchestrator pipeline.
    """
    # Setup task-specific logging
    task_logger = setup_task_logging(task_id)
    
    try:
        task_logger.info("orchestrator_background_started", task_id=task_id, idea=idea, industry=industry)
        
        # Update task status
        task_state.update_status(task_id, "running", 0.0, "initialization")
        
        # Initialize orchestrator
        orchestrator = GTMForgeOrchestrator()
        
        # Run pipeline with progress updates
        await orchestrator.run_with_progress(
            idea=idea,
            industry=industry,
            progress_callback=lambda stage, progress: update_task_progress(task_id, stage, progress)
        )
        
        # Get final results
        pipeline_state = orchestrator.get_pipeline_state()
        
        # Run QA validation
        task_state.update_status(task_id, "running", 90.0, "qa_validation")
        from app.agents.qa_agent.agent import QAAgent
        qa_agent = QAAgent()
        qa_report = await qa_agent.run(pipeline_state)
        
        # Run Publisher
        task_state.update_status(task_id, "running", 95.0, "publishing")
        from app.agents.publisher_agent.agent import PublisherAgent
        publisher_agent = PublisherAgent(task_id=task_id)
        publish_output = await publisher_agent.run(pipeline_state)
        
        # Store results
        result = {
            "manifest": publish_output.dict(),
            "qa_report": qa_report.dict(),
            "pipeline_state": pipeline_state.dict()
        }
        task_state.set_result(task_id, result)
        task_state.update_status(task_id, "completed", 100.0, "completed")
        
        task_logger.info("orchestrator_background_completed", task_id=task_id)
        
    except Exception as e:
        error_msg = f"Pipeline execution failed: {str(e)}"
        task_logger.error("orchestrator_background_failed", task_id=task_id, error=error_msg)
        
        task_state.set_error(task_id, error_msg)
        task_state.update_status(task_id, "failed", 0.0, "failed")


def update_task_progress(task_id: str, stage: str, progress: float):
    """
    Update task progress and send WebSocket message.
    """
    task_state.update_status(task_id, "running", progress, stage)
    
    # Send WebSocket update
    asyncio.create_task(manager.send_to_task(task_id, {
        "type": "progress",
        "task_id": task_id,
        "stage": stage,
        "progress": progress,
        "timestamp": datetime.now().isoformat()
    }))


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    # Clean up old logs
    cleaned = cleanup_task_logs(max_age_hours=24)
    print(f"Cleaned up {cleaned} old log files")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("GTMForge API shutting down")


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
