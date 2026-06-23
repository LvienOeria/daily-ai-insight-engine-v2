"""Lightweight MCP client for calling the web-search MCP server from the pipeline.

Spawns the MCP server as a subprocess and communicates via stdio.
"""

from __future__ import annotations

import sys
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


class MCPSearchClient:
    """Async client that wraps the web-search MCP server."""

    def __init__(self, server_module: str = "daily_ai_insight.mcp_search"):
        self.server_module = server_module
        self._session: ClientSession | None = None
        self._stack: Any = None

    async def __aenter__(self):
        import contextlib

        self._stack = contextlib.AsyncExitStack()
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", self.server_module],
        )
        transport = await self._stack.enter_async_context(stdio_client(server_params))
        read, write = transport
        self._session = await self._stack.enter_async_context(ClientSession(read, write))
        await self._session.initialize()
        return self

    async def __aexit__(self, *args: object):
        if self._stack:
            await self._stack.aclose()
        self._session = None
        self._stack = None

    async def search_ai_news(
        self,
        *,
        site: str,
        query: str = "",
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Call the search_ai_news MCP tool."""
        if self._session is None:
            raise RuntimeError("MCPSearchClient not initialized. Use async with.")
        result = await self._session.call_tool(
            "search_ai_news",
            {
                "site": site,
                "query": query,
                "max_results": max_results,
            },
        )
        if result.content:
            import json

            text = result.content[0].text
            # Handle error responses from the MCP server
            if text.startswith("Error executing tool"):
                raise RuntimeError(text)
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                # Fallback: try Python repr
                try:
                    import ast
                    return ast.literal_eval(text)
                except (ValueError, SyntaxError):
                    return []
        return []

    async def fetch_article_content(self, *, url: str) -> dict[str, Any]:
        """Call the fetch_article_content MCP tool."""
        if self._session is None:
            raise RuntimeError("MCPSearchClient not initialized. Use async with.")
        result = await self._session.call_tool(
            "fetch_article_content",
            {"url": url},
        )
        if result.content:
            import json

            return json.loads(result.content[0].text)
        return {}


def search_sync(site: str, query: str = "", max_results: int = 10) -> list[dict[str, Any]]:
    """Synchronous wrapper for calling the MCP web search tool.

    Use this from non-async pipeline code.
    """
    import asyncio

    async def _call():
        async with MCPSearchClient() as client:
            return await client.search_ai_news(
                site=site,
                query=query,
                max_results=max_results,
            )

    return asyncio.run(_call())
