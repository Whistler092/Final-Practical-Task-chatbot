from __future__ import annotations

import asyncio
from pathlib import Path
from typing import List

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient


class MCPStackProvider:
    """Loads LangChain tools from the custom disasters MCP server (stdio transport)."""

    def __init__(self, *, tool_name_prefix: bool = False) -> None:
        self._tool_name_prefix = tool_name_prefix

    def _client(self) -> MultiServerMCPClient:
        print(Path(__file__).resolve().parent.parent)
        server_dir = str(Path(__file__).resolve().parent.parent / "disasters-server")
        return MultiServerMCPClient(
            {
                "disasters": {
                    "transport": "stdio",
                    "command": "uv",
                    "args": ["--directory", server_dir, "run", "disasters-server"],
                },
            },
            tool_name_prefix=self._tool_name_prefix,
        )

    async def _async_get_tools(self) -> List[BaseTool]:
        return await self._client().get_tools()

    def get_tools(self) -> List[BaseTool]:
        """Synchronous entrypoint for Streamlit and other sync callers."""
        return asyncio.run(self._async_get_tools())
