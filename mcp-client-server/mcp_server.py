#!/usr/bin/env python3
"""
MCP Server with Document Processing Tools

This server exposes two tools:
1. get_recipient_suggestion - Analyzes document content and suggests recipients
2. improve_document - Improves document quality using AI
"""

import asyncio
import logging
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import cohere
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Cohere client
cohere_client = cohere.Client(api_key=Config.COHERE_API_KEY)

# Create MCP server instance
app = Server(Config.MCP_SERVER_NAME)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_recipient_suggestion",
            description="Analyzes document content and suggests appropriate recipients from a predefined list",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The document content to analyze"
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="improve_document",
            description="Improves document quality by fixing grammar, enhancing clarity, and improving structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The document content to improve"
                    }
                },
                "required": ["content"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    logger.info(f"Tool called: {name}")
    
    if name == "get_recipient_suggestion":
        return await get_recipient_suggestion(arguments.get("content", ""))
    elif name == "improve_document":
        return await improve_document(arguments.get("content", ""))
    else:
        raise ValueError(f"Unknown tool: {name}")


async def get_recipient_suggestion(content: str) -> list[TextContent]:
    """
    Analyze document content and suggest appropriate recipients.
    
    Args:
        content: Document content to analyze
        
    Returns:
        List of TextContent with recipient suggestions and reasoning
    """
    try:
        # Create prompt for Cohere
        prompt = f"""You are a document distribution expert. Analyze the following document and suggest appropriate recipients from this list:
{', '.join(Config.VALID_RECIPIENTS)}

Document:
{content}

Based on the content, determine which recipients should receive this document. Consider:
- Subject matter (legal, HR, financial, technical, etc.)
- Sensitivity level
- Required action or awareness
- Organizational impact

Respond in JSON format:
{{
    "recipients": ["recipient1", "recipient2"],
    "reasoning": "Brief explanation of why these recipients were chosen"
}}

Only include recipients from the provided list. Be specific and selective."""

        # Call Cohere API
        response = cohere_client.chat(
            model=Config.COHERE_MODEL,
            message=prompt,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result = response.text
        logger.info(f"Recipient suggestion result: {result}")
        
        return [TextContent(
            type="text",
            text=result
        )]
        
    except Exception as e:
        logger.error(f"Error in get_recipient_suggestion: {e}")
        error_response = {
            "recipients": [],
            "reasoning": f"Error occurred: {str(e)}",
            "error": str(e)
        }
        return [TextContent(
            type="text",
            text=str(error_response)
        )]


async def improve_document(content: str) -> list[TextContent]:
    """
    Improve document quality using AI.
    
    Args:
        content: Document content to improve
        
    Returns:
        List of TextContent with improved document and summary of changes
    """
    try:
        # Create prompt for Cohere
        prompt = f"""You are a professional document editor. Improve the following document by:
1. Fixing grammar and spelling errors
2. Enhancing clarity and readability
3. Improving sentence structure and flow
4. Maintaining the original meaning and tone
5. Making it more professional and polished

Original Document:
{content}

Respond in JSON format:
{{
    "improved_content": "The improved version of the document",
    "changes_summary": "Brief summary of the main improvements made"
}}"""

        # Call Cohere API
        response = cohere_client.chat(
            model=Config.COHERE_MODEL,
            message=prompt,
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        result = response.text
        logger.info(f"Document improvement completed")
        
        return [TextContent(
            type="text",
            text=result
        )]
        
    except Exception as e:
        logger.error(f"Error in improve_document: {e}")
        error_response = {
            "improved_content": content,
            "changes_summary": f"Error occurred: {str(e)}",
            "error": str(e)
        }
        return [TextContent(
            type="text",
            text=str(error_response)
        )]


async def main():
    """Run the MCP server."""
    logger.info(f"Starting MCP server: {Config.MCP_SERVER_NAME} v{Config.MCP_SERVER_VERSION}")
    logger.info(f"Using Cohere model: {Config.COHERE_MODEL}")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
