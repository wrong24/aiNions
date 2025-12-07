import os
import logging
import json
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field
from typing import Optional

from app.schemas import InputMessage, OrchestrationState
from app.graph import NionGraph
from app.formatter import NionFormatter

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global graph instance
_graph_instance = None


def get_graph() -> NionGraph:
    """Get or initialize the NionGraph"""
    global _graph_instance
    if _graph_instance is None:
        logger.info("Initializing NionGraph...")
        _graph_instance = NionGraph()
        logger.info("NionGraph initialized successfully")
    return _graph_instance


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager"""
    logger.info("Nion Orchestration Engine starting...")
    # Startup
    graph = get_graph()
    logger.info("Graph initialized and ready for requests")

    yield

    # Shutdown
    logger.info("Nion Orchestration Engine shutting down...")


# FastAPI app
app = FastAPI(
    title="Nion Orchestration Engine",
    description="Hierarchical AI orchestration engine with LangGraph",
    version="1.0.0",
    lifespan=lifespan
)


class ProcessRequest(BaseModel):
    """Request model for /process endpoint"""
    message: str = Field(..., description="The message to process")
    sender: str = Field(..., description="The sender of the message")
    project_id: str = Field(..., description="The project ID")
    message_id: Optional[str] = Field(None, description="Optional unique message ID")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "The customer demo went great! They loved it but asked if we could add real-time notifications.",
                "sender": "Sarah Chen",
                "project_id": "PRJ-ALPHA",
                "message_id": "MSG-20241206-001"
            }
        }


class ProcessResponse(BaseModel):
    """Response model for /process endpoint"""
    state_id: str
    status: str
    message: str
    execution_time_ms: float
    execution_results_count: int


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Nion Orchestration Engine"
    })


@app.post("/process", response_model=ProcessResponse)
async def process_message(request: ProcessRequest):
    """Process a message through the Nion orchestration engine"""

    start_time = datetime.utcnow()

    try:
        logger.info(f"Processing message from {request.sender}")

        # Create input message
        input_message = InputMessage(
            message=request.message,
            sender=request.sender,
            project_id=request.project_id,
            message_id=request.message_id,
            timestamp=datetime.utcnow()
        )

        # Get graph and invoke
        graph = get_graph()
        result_state = graph.invoke(input_message)

        execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        logger.info(f"Message processed successfully: {result_state.state_id}")

        return ProcessResponse(
            state_id=result_state.state_id,
            status="COMPLETED",
            message="Orchestration completed successfully",
            execution_time_ms=execution_time_ms,
            execution_results_count=len(result_state.execution_results)
        )

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )


@app.post("/process/nion-map")
async def process_message_with_map(request: ProcessRequest):
    """Process a message and return the NION ORCHESTRATION MAP"""

    start_time = datetime.utcnow()

    try:
        logger.info(f"Processing message from {request.sender} (with map output)")

        # Create input message
        input_message = InputMessage(
            message=request.message,
            sender=request.sender,
            project_id=request.project_id,
            message_id=request.message_id,
            timestamp=datetime.utcnow()
        )

        # Get graph and invoke - using direct orchestration instead of LangGraph
        graph = get_graph()
        result_state = graph.invoke_simple(input_message)

        execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Format output
        nion_map = NionFormatter.generate_nion_map(result_state)

        logger.info(f"NION map generated for state: {result_state.state_id}")

        return PlainTextResponse(
            content=nion_map,
            headers={
                "X-State-ID": result_state.state_id,
                "X-Execution-Time-Ms": str(execution_time_ms),
                "X-Tasks-Executed": str(len(result_state.execution_results))
            }
        )

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )


@app.post("/process/json")
async def process_message_with_json(request: ProcessRequest):
    """Process a message and return detailed JSON output"""

    start_time = datetime.utcnow()

    try:
        logger.info(f"Processing message from {request.sender} (with JSON output)")

        # Create input message
        input_message = InputMessage(
            message=request.message,
            sender=request.sender,
            project_id=request.project_id,
            message_id=request.message_id,
            timestamp=datetime.utcnow()
        )

        # Get graph and invoke
        graph = get_graph()
        result_state = graph.invoke(input_message)

        execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Format output
        json_output = NionFormatter.generate_json_output(result_state)
        json_output["execution_time_ms"] = execution_time_ms

        logger.info(f"JSON output generated for state: {result_state.state_id}")

        return JSONResponse(
            content=json_output,
            headers={
                "X-State-ID": result_state.state_id,
                "X-Execution-Time-Ms": str(execution_time_ms)
            }
        )

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return JSONResponse({
        "service": "Nion Orchestration Engine",
        "version": "1.0.0",
        "description": "Hierarchical AI orchestration engine with LangGraph",
        "endpoints": {
            "GET /health": "Health check",
            "POST /process": "Process message (JSON response)",
            "POST /process/nion-map": "Process message (NION MAP text response)",
            "POST /process/json": "Process message (Detailed JSON response)",
            "GET /": "This endpoint"
        }
    })


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting Nion API server on {host}:{port}")
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
