import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
    SMITHERY_API_KEY  = os.getenv("SMITHERY_API_KEY")

    MAX_ITERATIONS = 3
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # MCP Server URLs
    FETCH_MCP_URL = "https://smithery.ai/server/fetch-mcp/api"
    BRAVE_SEARCH_MCP_URL = "https://smithery.ai/server/@smithery-ai/brave-search/api"

settings = Settings()
