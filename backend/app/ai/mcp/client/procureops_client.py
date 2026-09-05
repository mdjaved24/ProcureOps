import json
import logging
from typing import Dict, Any, Optional
from mcp import Client

from app.ai.mcp.server.procureops_server import mcp

logger = logging.getLogger(__name__)


class ProcureOpsMCPClient:
    """MCP Client for ProcureOps operations."""
    
    @staticmethod
    async def list_tools() -> list[dict]:
        """List all available MCP tools."""
        async with Client(mcp, raise_exceptions=True) as client:
            tools_result = await client.list_tools()
            
            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                }
                for tool in tools_result.tools
            ]
    
    @staticmethod
    async def call_tool(
        tool_name: str,
        arguments: dict,
    ) -> dict:
        """
        Call an MCP tool with the given arguments.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments for the tool
            
        Returns:
            dict: {
                "success": bool,
                "data": Any,
                "error": str | None
            }
        """
        logger.info(f"Calling MCP tool: {tool_name} with args: {arguments}")
        
        try:
            async with Client(mcp, raise_exceptions=True) as client:
                result = await client.call_tool(tool_name, arguments)
                
                # Handle MCP tool error
                if result.is_error:
                    return {
                        "success": False,
                        "error": str(result),
                        "data": None,
                    }
                
                # Parse MCP content
                for content in result.content:
                    if hasattr(content, "text"):
                        try:
                            parsed_data = json.loads(content.text)
                            return {
                                "success": True,
                                "data": parsed_data,
                            }
                        except json.JSONDecodeError:
                            return {
                                "success": False,
                                "error": "Invalid JSON returned from MCP tool",
                                "data": None,
                            }
                
                # No content returned
                return {
                    "success": False,
                    "error": "No usable response returned from MCP tool",
                    "data": None,
                }
                
        except Exception as e:
            logger.error(f"MCP tool error: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None,
            }