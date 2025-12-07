#!/usr/bin/env python3
"""
MCP Client for Document Processing Tools

This client connects to the MCP server and provides methods to invoke tools.
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPClient:
    """MCP Client for connecting to document processing tools."""
    
    def __init__(self, server_script_path: str = "mcp_server.py"):
        """
        Initialize MCP client.
        
        Args:
            server_script_path: Path to the MCP server script
        """
        self.server_script_path = server_script_path
        self.session: Optional[ClientSession] = None
        self.available_tools: Dict[str, Any] = {}
        
    @asynccontextmanager
    async def connect(self):
        """
        Connect to the MCP server.
        
        Yields:
            ClientSession: Active MCP client session
        """
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script_path],
            env=None
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                
                # Initialize the session
                await session.initialize()
                logger.info("MCP client connected and initialized")
                
                # List available tools
                tools_response = await session.list_tools()
                self.available_tools = {
                    tool.name: tool for tool in tools_response.tools
                }
                logger.info(f"Available tools: {list(self.available_tools.keys())}")
                
                yield session
                
                self.session = None
                logger.info("MCP client disconnected")
    
    async def get_recipient_suggestion(self, content: str) -> Dict[str, Any]:
        """
        Get recipient suggestions for a document.
        
        Args:
            content: Document content to analyze
            
        Returns:
            Dictionary with recipients and reasoning
        """
        if not self.session:
            raise RuntimeError("Client not connected. Use 'async with client.connect()' first.")
        
        try:
            result = await self.session.call_tool(
                "get_recipient_suggestion",
                arguments={"content": content}
            )
            
            # Parse the response
            if result.content and len(result.content) > 0:
                response_text = result.content[0].text
                return json.loads(response_text)
            else:
                return {
                    "recipients": [],
                    "reasoning": "No response from tool",
                    "error": "Empty response"
                }
                
        except Exception as e:
            logger.error(f"Error calling get_recipient_suggestion: {e}")
            return {
                "recipients": [],
                "reasoning": f"Error: {str(e)}",
                "error": str(e)
            }
    
    async def improve_document(self, content: str) -> Dict[str, Any]:
        """
        Improve document quality.
        
        Args:
            content: Document content to improve
            
        Returns:
            Dictionary with improved content and changes summary
        """
        if not self.session:
            raise RuntimeError("Client not connected. Use 'async with client.connect()' first.")
        
        try:
            result = await self.session.call_tool(
                "improve_document",
                arguments={"content": content}
            )
            
            # Parse the response
            if result.content and len(result.content) > 0:
                response_text = result.content[0].text
                return json.loads(response_text)
            else:
                return {
                    "improved_content": content,
                    "changes_summary": "No response from tool",
                    "error": "Empty response"
                }
                
        except Exception as e:
            logger.error(f"Error calling improve_document: {e}")
            return {
                "improved_content": content,
                "changes_summary": f"Error: {str(e)}",
                "error": str(e)
            }
    
    async def list_tools(self) -> Dict[str, Any]:
        """
        List all available tools.
        
        Returns:
            Dictionary of available tools
        """
        if not self.session:
            raise RuntimeError("Client not connected. Use 'async with client.connect()' first.")
        
        return {
            name: {
                "description": tool.description,
                "inputSchema": tool.inputSchema
            }
            for name, tool in self.available_tools.items()
        }


async def main():
    """Example usage of the MCP client."""
    client = MCPClient()
    
    async with client.connect():
        # Test get_recipient_suggestion
        print("\n=== Testing get_recipient_suggestion ===")
        test_doc = """
        We need to review the new employee benefits package to ensure compliance 
        with labor laws. The package includes health insurance, retirement plans, 
        and paid time off policies. Legal review is required before implementation.
        """
        
        result = await client.get_recipient_suggestion(test_doc)
        print(f"Recipients: {result.get('recipients', [])}")
        print(f"Reasoning: {result.get('reasoning', 'N/A')}")
        
        # Test improve_document
        print("\n=== Testing improve_document ===")
        test_doc2 = """
        this document need to be more better and clear for everyone to understand 
        it good. we should make sure its professional and easy to read.
        """
        
        result = await client.improve_document(test_doc2)
        print(f"Improved: {result.get('improved_content', 'N/A')}")
        print(f"Changes: {result.get('changes_summary', 'N/A')}")
        
        # List tools
        print("\n=== Available Tools ===")
        tools = await client.list_tools()
        for name, info in tools.items():
            print(f"- {name}: {info['description']}")


if __name__ == "__main__":
    asyncio.run(main())
