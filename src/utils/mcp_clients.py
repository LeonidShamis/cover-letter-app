import aiohttp
import asyncio
from typing import Dict, Any
from src.config.settings import settings

class MCPClient:
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

class FetchMCPClient(MCPClient):
    async def fetch_url_content(self, url: str) -> str:
        """Fetch content from URL using Fetch MCP server"""
        try:
            payload = {
                "method": "fetch",
                "params": {
                    "url": url,
                    "format": "markdown"
                }
            }
            
            async with self.session.post(
                settings.FETCH_MCP_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("content", "")
                else:
                    return f"Error fetching content: {response.status}"
        except Exception as e:
            return f"Error: {str(e)}"

class BraveSearchMCPClient(MCPClient):
    async def search_company(self, company_name: str) -> Dict[str, Any]:
        """Search for company information using Brave Search MCP server"""
        try:
            payload = {
                "method": "search",
                "params": {
                    "query": f"{company_name} company profile culture values",
                    "count": 5
                }
            }
            
            async with self.session.post(
                settings.BRAVE_SEARCH_MCP_URL,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.BRAVE_API_KEY}"
                }
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Search failed: {response.status}"}
        except Exception as e:
            return {"error": str(e)}
