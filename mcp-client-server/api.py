#!/usr/bin/env python3
"""
FastAPI REST API for MCP Document Processing Tools

This API exposes HTTP endpoints that use the MCP client to invoke document processing tools.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from mcp_client import MCPClient
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global MCP client instance
mcp_client: MCPClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage MCP client lifecycle."""
    global mcp_client
    
    logger.info("Starting API server...")
    mcp_client = MCPClient()
    
    # Connect to MCP server
    async with mcp_client.connect():
        logger.info("MCP client connected")
        yield
    
    logger.info("Shutting down API server...")


# Create FastAPI app
app = FastAPI(
    title="MCP Document Processing API",
    description="REST API for document processing using MCP tools and Cohere AI",
    version="1.0.0",
    lifespan=lifespan
)


# Request/Response Models
class DocumentRequest(BaseModel):
    """Request model for document processing."""
    content: str = Field(
        ...,
        description="The document content to process",
        min_length=1,
        examples=["This is a sample document about employee benefits."]
    )


class RecipientResponse(BaseModel):
    """Response model for recipient suggestions."""
    recipients: list[str] = Field(
        description="List of suggested recipients"
    )
    reasoning: str = Field(
        description="Explanation of why these recipients were chosen"
    )
    error: str | None = Field(
        default=None,
        description="Error message if any"
    )


class ImproveResponse(BaseModel):
    """Response model for document improvement."""
    improved_content: str = Field(
        description="The improved version of the document"
    )
    changes_summary: str = Field(
        description="Summary of the main improvements made"
    )
    error: str | None = Field(
        default=None,
        description="Error message if any"
    )


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    mcp_connected: bool
    available_tools: list[str]


class ToolInfo(BaseModel):
    """Information about an MCP tool."""
    description: str
    inputSchema: Dict[str, Any]


# API Endpoints

@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "MCP Document Processing API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "tools": "/tools",
            "recipients": "/api/recipients",
            "improve": "/api/improve",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint."""
    try:
        tools = await mcp_client.list_tools()
        return HealthResponse(
            status="healthy",
            mcp_connected=True,
            available_tools=list(tools.keys())
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            mcp_connected=False,
            available_tools=[]
        )


@app.get("/tools", response_model=Dict[str, ToolInfo], tags=["General"])
async def list_tools():
    """List all available MCP tools."""
    try:
        tools = await mcp_client.list_tools()
        return tools
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tools: {str(e)}"
        )


@app.post("/api/recipients", response_model=RecipientResponse, tags=["Document Processing"])
async def get_recipients(request: DocumentRequest):
    """
    Get recipient suggestions for a document.
    
    Analyzes the document content and suggests appropriate recipients
    from a predefined list based on the subject matter, sensitivity,
    and organizational impact.
    """
    try:
        logger.info("Processing recipient suggestion request")
        result = await mcp_client.get_recipient_suggestion(request.content)
        
        return RecipientResponse(
            recipients=result.get("recipients", []),
            reasoning=result.get("reasoning", ""),
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"Error getting recipient suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recipient suggestions: {str(e)}"
        )


@app.post("/api/improve", response_model=ImproveResponse, tags=["Document Processing"])
async def improve_document(request: DocumentRequest):
    """
    Improve document quality.
    
    Enhances the document by fixing grammar, improving clarity,
    and making it more professional while maintaining the original
    meaning and tone.
    """
    try:
        logger.info("Processing document improvement request")
        result = await mcp_client.improve_document(request.content)
        
        return ImproveResponse(
            improved_content=result.get("improved_content", request.content),
            changes_summary=result.get("changes_summary", ""),
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"Error improving document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to improve document: {str(e)}"
        )


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "error": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {Config.API_HOST}:{Config.API_PORT}")
    uvicorn.run(
        "api:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True,
        log_level="info"
    )
